"""API for worlty integration."""

import asyncio
from collections import defaultdict
import json
from typing import Any

from homeassistant.components.binary_sensor import BinarySensorEntityDescription
from homeassistant.components.climate import ClimateEntityDescription
from homeassistant.components.fan import FanEntityDescription
from homeassistant.components.light import LightEntityDescription
from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.components.switch import SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity, generate_entity_id

from .const import (
    DOMAIN,
    LOGGER,
    MANUFACTURER,
    get_worlty_description,
    map_worlty_state,
    map_worlty_sub,
    map_worlty_to_platform,
)


def map_worlty_entity_description(
    worlty_type: int, worlty_class: int, worlty_sub: str
) -> tuple:
    """Map for Worlty entity description."""
    key, device_class, icon, unit_of_measurement = get_worlty_description(
        worlty_type, worlty_class
    )
    if key is None:
        return None, "unknown"

    platform_type = map_worlty_to_platform(worlty_type)
    entity_description_cls = {
        Platform.BINARY_SENSOR: BinarySensorEntityDescription,
        Platform.CLIMATE: ClimateEntityDescription,
        Platform.FAN: FanEntityDescription,
        Platform.LIGHT: LightEntityDescription,
        Platform.SENSOR: SensorEntityDescription,
        Platform.SWITCH: SwitchEntityDescription,
    }.get(platform_type)

    if entity_description_cls:
        if unit_of_measurement is not None:
            description = entity_description_cls(
                key=key,
                has_entity_name=True,
                icon=icon,
                device_class=device_class,
                translation_key=key,
                translation_placeholders={"sub_id": worlty_sub},
                native_unit_of_measurement=unit_of_measurement,
            )
        else:
            description = entity_description_cls(
                key=key,
                has_entity_name=True,
                icon=icon,
                device_class=device_class,
                translation_key=key,
                translation_placeholders={"sub_id": worlty_sub},
            )
        return description, key

    return None, "unknown"


class WorltyLocal:
    """Worlty local API."""

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        port: int,
        access_token: str,
        async_event_handler,
    ) -> None:
        """Initialize."""
        self.hass = hass
        self._entry: ConfigEntry = None
        self._host: str = host
        self._port: int = port
        self._access_token: str = access_token
        self._subscribe = None
        self._publish = None
        self._async_event_handler = async_event_handler
        self._disconnect = False
        self._connected = False
        self._reconnect = False
        self._queue = []

        self._add_entity_listeners: dict[Platform, Any] = defaultdict()
        self._entity_map: dict[str, dict[str, Any]] = {}
        self._entities: dict[Platform, dict[str, dict[str, Any]]] = defaultdict(dict)
        self._worlty_devices = []
        self.worlty_pad: WorltyBaseDevice = None
        self.worlty_entity: dict[str, WorltyBaseEntity] = {}
        self.worlty_entities: dict[Platform, list[WorltyBaseEntity]] = defaultdict(list)

    @classmethod
    async def create(
        cls,
        hass: HomeAssistant,
        host: str,
        port: int,
        access_token: str,
        async_event_handler,
    ):
        """Create Worlty API."""
        instance = cls(hass, host, port, access_token, async_event_handler)

        return instance

    async def _connect(self):
        """Connnect device."""
        try:
            LOGGER.debug(
                f"[{self.worlty_pad.device_id if self.worlty_pad is not None else self._host}] Try connect to {self._host}:{self._port}"
            )
            self._subscribe, self._publish = await asyncio.open_connection(
                self._host, self._port
            )
            self._connected = True
            LOGGER.debug(
                f"[{self.worlty_pad.device_id if self.worlty_pad is not None else self._host}] Connected to {self._host}:{self._port}"
            )
        except OSError as e:
            if self.worlty_pad is not None:
                self.worlty_pad.device_available = False
            LOGGER.debug(
                f"[{self.worlty_pad.device_id if self.worlty_pad is not None else self._host}] Can not connect to {self._host}:{self._port}, error: {e}"
            )
            return False
        return True

    def terminate(self):
        """Terminate connection."""
        if self._publish is not None:
            if self.worlty_pad is not None:
                self.worlty_pad.device_available = False
            self._publish.close()

    async def disconnect(self):
        """Disconnect device."""
        self._disconnect = True

    async def auth(self, entry: ConfigEntry = None):
        """Auth device."""
        if self._connected is False:
            connected = await self._connect()
            if self.worlty_pad is not None:
                self.worlty_pad.device_available = connected
            if connected is False:
                return connected, "cannot_connect"

        message: dict[str, Any] = await self.subscribe(5)
        if message.get("error") or message.get("type") is None:
            self.terminate()
            LOGGER.error(
                f"[{self.worlty_pad.device_id if self.worlty_pad is not None else self._host}] Can not auth device {self._host}:{self._port}, error: no_request, message: {message}"
            )
            return False, "unreachable"

        if message.get("type") == "auth_required":
            await asyncio.sleep(1)
            await self.publish({"type": "auth", "access_token": self._access_token})

        message = await self.subscribe(5)
        if message.get("error"):
            LOGGER.error(
                f"[{self.worlty_pad.device_id if self.worlty_pad is not None else self._host}] Can not auth device {self._host}:{self._port}, error: no_response, message: {message}"
            )
            return False, "unreachable"

        if message.get("type") == "authenticated":
            data: dict = message.get("data", {})
            if entry is None:
                LOGGER.debug(
                    f"[{self.worlty_pad.device_id if self.worlty_pad is not None else self._host}] Authenticated {self._host}:{self._port}, entry=None"
                )
                return True, data
            self._entry = entry

            self.worlty_pad = WorltyBaseDevice(data)
            device_registry = dr.async_get(self.hass)
            device_registry.async_get_or_create(
                config_entry_id=self._entry.entry_id,
                identifiers={(DOMAIN, self.worlty_pad.mac_address)},
                serial_number=self.worlty_pad.mac_address,
                manufacturer=self.worlty_pad.manufacturer,
                name=self.worlty_pad.device_id,
                model=self.worlty_pad.device_model,
                sw_version=self.worlty_pad.fw_version,
            )

            self._entity_map: dict[str, dict[str, Any]] = self.get_data("devices", {})
            for device in self._entity_map.copy().values():
                self.update_device(device)
            for k, v in data.items():
                self.set_data(k, v)
            LOGGER.debug(
                f"[{self.worlty_pad.device_id if self.worlty_pad is not None else self._host}] Authenticated {self._host}:{self._port}"
            )
            return True, None
        LOGGER.error(
            f"[{self.worlty_pad.device_id if self.worlty_pad is not None else self._host}] Auth failed {self._host}:{self._port} > {message}"
        )
        return False, "invalid_access_token"

    async def reauth(self) -> bool:
        """Retry auth."""
        if self._connected is False and self._disconnect is False:
            auth, _ = await self.auth()
            while not auth:
                if self._connected is True:
                    self._connected = False
                    self.terminate()
                await asyncio.sleep(5)
                auth, _ = await self.auth()

            if self.worlty_pad is not None:
                self.worlty_pad.device_available = auth
            if self.hass.data[DOMAIN]["task"] is not None:
                self.hass.data[DOMAIN]["task"].done()
            result = await self.get_worlty_devices()
            if result is None:
                self._connected = False
                self.terminate()
                return False
            self.hass.data[DOMAIN]["task"] = self.hass.loop.create_task(
                self.listen_for_message()
            )
            await asyncio.sleep(5)
            self._reconnect = True
            return True

    def set_data(self, name: str, value: Any) -> Any:
        """Set entry data."""
        if self._entry is None:
            return value
        new_data = {
            "ip_address": self._host,
            "port": self._port,
            "access_token": self._access_token,
            "version": self.worlty_pad.fw_version,
            "model": self.worlty_pad.device_model,
            "device_id": self.worlty_pad.device_id,
            "mac_address": self.worlty_pad.mac_address,
            "device": {},
        }
        new_data.update({name: value})
        self.hass.config_entries.async_update_entry(
            entry=self._entry,
            data=new_data,
        )
        return value

    def get_data(self, name: str, default_value=False) -> Any:
        """Get entry data."""
        if self._entry is None:
            return default_value
        return self._entry.data.get(name, default_value)

    async def publish(self, payload) -> bool:
        """Publish message."""
        message = json.dumps(payload)
        LOGGER.debug(
            f"[{self.worlty_pad.device_id if self.worlty_pad is not None else self._host}] Publish message : {message}"
        )
        self._publish.write(message.encode())
        await self._publish.drain()
        return True

    async def subscribe(self, timeout: float = None) -> dict[str, Any]:
        """Subscribe message."""
        try:
            buffer = b""
            merge = True
            while merge:
                chunk = await asyncio.wait_for(
                    self._subscribe.read(1024 * 30), timeout=timeout
                )
                if not chunk:
                    return {}
                buffer += chunk

                if buffer:
                    try:
                        message = buffer.decode().strip()
                        return json.loads(message)
                    except json.JSONDecodeError:
                        continue
        except TimeoutError:
            return {"error": "timeout"}
        return {}

    async def listen_for_message(self):
        """Listen for Wolrty message."""
        LOGGER.debug("Listen for Wolrty message")
        try:
            while self._connected:
                message: dict[str, Any] = await self.subscribe(0.1)
                if message.get("data"):
                    self.hass.loop.create_task(self.handle_message(message))
                elif message.get("error"):
                    continue
                else:
                    break
        except asyncio.CancelledError:
            LOGGER.debug("Listener cancelled")
        finally:
            if self.worlty_pad is not None:
                self.worlty_pad.device_available = False
            LOGGER.debug("Listener finished")
            self._connected = False
            self.terminate()
            await asyncio.sleep(1)
            if self._disconnect is False:
                LOGGER.debug("Try auth as listener finished")
                success = await self.reauth()
                while not success:
                    success = await self.reauth()

    async def handle_message(self, message: dict[str, Any]) -> None:
        """Handle Wolrty message."""
        data_type: str = message.get("type")
        data: dict[str, Any] = message.get("data", {})
        devices: list[dict] = data.get("devices")
        if data_type == "update" and all(
            isinstance(device, dict) for device in devices
        ):
            LOGGER.debug(
                f"[{self.worlty_pad.device_id if self.worlty_pad is not None else self._host}] Handle {len(devices)} devices"
            )
            devices = sorted(devices, key=lambda device: device.get("pk", 0))
            for device in devices:
                device["children"] = sorted(
                    device.get("children", []), key=lambda child: child.get("pk", 0)
                )
                for child in device["children"]:
                    child["fk"] = device.get("pk", 0)
                self.update_device(device)
            if len(devices) > 0:
                self.set_data("devices", self._entity_map.copy())
        elif data_type == "health":
            devices: dict[str, int] = data.get("devices")
            pks = [int(pk) for pk, _ in devices.items()]
            await self.publish({"type": "get", "data": {"devices": pks}})
        elif data_type == "device/list":
            # TODO 해당 데이터에 없는 entity 삭제
            await self.publish({"type": "get", "data": {"devices": devices}})
        elif data_type == "device/delete":
            # TODO 해당 데이터에 있는 entity 삭제
            LOGGER.debug(
                f"[{self.worlty_pad.device_id if self.worlty_pad is not None else self._host}] Delete devices : {message}"
            )
        else:
            LOGGER.debug(
                f"[{self.worlty_pad.device_id if self.worlty_pad is not None else self._host}] Unhandled message : {message}"
            )

    def get_worlty_entity(self, unique_id) -> dict[str, Any]:
        """Get entity."""
        return self._entity_map.get(unique_id)

    async def get_worlty_devices(self) -> dict[Platform, dict[str, dict[str, Any]]]:
        """Get devices from Worlty."""
        return self._entities

    def make_unique_id(self, pk: int, fk: int = 0, did: str = "") -> str:
        """Get unique id from worlty device."""
        return (
            f"{self.worlty_pad.device_id}:{pk}:{did}"
            if fk == 0
            else f"{self.worlty_pad.device_id}:{fk}_{pk}:{did}"
        )

    def update_device(self, device: dict[str, Any]) -> None:
        """Update device or append if not exists in _devices."""
        self._update_or_create_worlty_entity(device)
        for child in device.get("children", []):
            if child.get("hide") is not True:
                child["parent_unique_id"] = self.make_unique_id(
                    device.get("pk"), 0, device.get("did")
                )
                self._update_or_create_worlty_entity(child)

    def _update_or_create_worlty_entity(self, device: dict[str, Any]) -> None:
        """Create the device map."""
        pk: int = device.get("pk", 0)
        fk: int = device.get("fk", 0)
        unique_id = self.make_unique_id(pk, fk, device.get("did" if fk == 0 else "cid"))
        worlty_entity: WorltyBaseEntity = self.worlty_entity.get(unique_id)
        if worlty_entity is not None:
            self._entity_map.update({unique_id: device})
            worlty_entity.update_entity(device)
        else:
            entity = self._entity_map.setdefault(unique_id, device)
            entity.update(device)
            entity_platform: Platform = map_worlty_to_platform(entity.get("type"))
            if entity_platform is not None:
                entity = self._entities[entity_platform].setdefault(unique_id, device)
                entity.update(device)
                add_entity_callback = self._add_entity_listeners.get(entity_platform)
                if add_entity_callback is not None:
                    add_entity_callback(entity)

    def register_entity(self, worlty_entity: "WorltyBaseEntity"):
        """Register entity to worlty_entity."""
        if worlty_entity.worlty_type is not None:
            self.worlty_entity[worlty_entity.worlty_unique_id] = worlty_entity
            self.worlty_entities[worlty_entity.worlty_type].append(worlty_entity)

    def register_add_listener(self, entity_type: Platform, cb: callback) -> None:
        """Register async add entities callback."""
        self._add_entity_listeners[entity_type] = cb

    async def loop(self) -> None:
        """Loop for publish payload."""
        await asyncio.sleep(0.1)
        if len(self._queue) > 0:
            await self.publish(
                {
                    "type": "set",
                    "data": {"devices": self._queue},
                }
            )
            await self.publish(self._queue)
            self.deque()

    def queue(self, data) -> None:
        """Queue message."""
        self._queue = [q for q in self._queue if q.get("pk") != data.get("pk")]
        self._queue.append(data)

        if self.hass.data[DOMAIN].get("loop") is not None:
            self.hass.data[DOMAIN]["loop"].cancel()

        self.hass.data[DOMAIN]["loop"] = self.hass.loop.create_task(self.loop())

    def deque(self) -> None:
        """Deque message."""
        if len(self._queue) > 0:
            self._queue.clear()


class WorltyBaseDevice:
    """Worlty device class."""

    device_id: str
    device_model: str
    mac_address: str
    fw_version: str
    device_available: bool

    def __init__(self, device_info: dict[str, Any]) -> None:
        """Initialize an worlty device."""
        self.device_id = device_info.get("device_id")
        self.device_model = device_info.get("model")
        self.mac_address = device_info.get("mac_address")
        self.manufacturer = MANUFACTURER
        self.fw_version = device_info.get("version")
        self.device_available = True

    def __repr__(self) -> str:
        """Return a string representation of Worlty device."""
        return f"Worlty(model={self.device_model}, id={self.device_id}, mac_address={self.mac_address}, fw_version={self.fw_version})"


class WorltyBaseEntity(Entity):
    """Worlty entity class."""

    coordinator: WorltyLocal
    worlty_entity_info: dict[str, Any]
    worlty_worlty_is_child: bool
    worlty_parent: int
    worlty_parent_unique_id: str
    worlty_unique_id: str
    worlty_pk: int
    worlty_name: str
    worlty_sub: str
    worlty_type: Platform
    worlty_class: int
    worlty_state: Any
    worlty_last_changed_time: int
    worlty_attribute: dict[str, Any]
    _loaded: bool
    _update_entity: callback

    def __init__(
        self,
        coordinator: "WorltyLocal",
        entity_info: dict[str, Any],
        entity_update: callback,
    ) -> None:
        """Initialize an worlty entity."""
        self.coordinator = coordinator
        self.hass = coordinator.hass
        self.entity_info = entity_info
        self.worlty_is_child = entity_info.get("fk", 0) > 0
        self.worlty_parent = entity_info.get("fk", 0)
        self.worlty_parent_unique_id = entity_info.get(
            "parent_unique_id", self.worlty_parent
        )
        self.worlty_pk = entity_info.get("pk")
        if not self.worlty_is_child:
            self.worlty_name = entity_info.get("did")
            self.worlty_sub = map_worlty_sub(
                self.hass.config.language, self.worlty_name.split("_")[1]
            )
        else:
            parent_sub = (
                self.coordinator.get_worlty_entity(self.worlty_parent_unique_id)
                .get("did")
                .split("_")[1]
            )
            self.worlty_name = entity_info.get("cid")
            self.worlty_sub = f"{map_worlty_sub(self.hass.config.language, self.worlty_name)}({map_worlty_sub(self.hass.config.language,parent_sub)})"
        self.worlty_unique_id = coordinator.make_unique_id(
            self.worlty_pk, self.worlty_parent, self.worlty_name
        )
        self.worlty_type = entity_info.get("type")
        self.worlty_class = entity_info.get("cls")
        self.worlty_state = map_worlty_state(
            self.hass.config.language, entity_info.get("stt")
        )
        self.worlty_last_changed_time = entity_info.get("lct")
        self.worlty_attribute = entity_info.get("payload")

        self._update_entity = entity_update
        self._loaded = False
        self._attr_unique_id = self.worlty_unique_id.lower()
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.worlty_pad.mac_address)},
        )

        description, key = map_worlty_entity_description(
            self.worlty_type, self.worlty_class, self.worlty_sub
        )
        self.entity_id = generate_entity_id(
            "worlty.{}",
            f"Worlty {key} {self.worlty_sub}",
            hass=self.coordinator.hass,
        )
        self.entity_description = description

        self.coordinator.register_entity(self)
        LOGGER.debug(
            f"Initialize a worlty entity -> {repr(self)}, {self.entity_description}"
        )

    def __repr__(self) -> str:
        """Return a string representation of Worlty entity."""
        return f"{'WorltyEntity' if not self.worlty_is_child else 'WorltyChild'}(id={self.worlty_unique_id}, name={self.worlty_name}, type={self.worlty_type}, class={map_worlty_to_platform(self.worlty_type)})"

    async def async_added_to_hass(self):
        """Call when entity is added to hass."""
        self._loaded = True
        self._update_callback()

    def _update_callback(self):
        """Update the state."""
        if self._update_entity is not None:
            self._update_entity()
        self.schedule_update_ha_state()

    def update_entity(self, entity_info: dict[str, Any]) -> None:
        """Update entity info."""
        if self._loaded is True:
            if "payload" in entity_info:
                self.worlty_state = map_worlty_state(
                    self.hass.config.language, entity_info.get("stt")
                )
                self.worlty_last_changed_time = entity_info.get("lct")
                self.worlty_attribute.update(entity_info.get("payload"))
                self._update_callback()

    async def set_device(self, **kwargs: Any) -> None:
        """Publish set device."""
        self.coordinator.queue(
            {
                "pk": self.worlty_pk,
                "payload": {**kwargs},
            }
        )

    @property
    def available(self):
        """Return True if device is available."""
        return (
            self.coordinator.worlty_pad.device_available
            if self.coordinator.worlty_pad is not None
            else self._loaded
        )

    @property
    def should_poll(self) -> bool:
        """No polling needed for this device."""
        return False
