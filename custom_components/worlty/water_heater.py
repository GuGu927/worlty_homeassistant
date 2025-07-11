"""Worlty water heater."""

from typing import Any

from homeassistant.components.climate import (
    PRESET_AWAY,
    PRESET_BOOST,
    PRESET_ECO,
    PRESET_SLEEP,
    HVACMode,
)
from homeassistant.components.water_heater import (
    STATE_GAS,
    STATE_OFF,
    WaterHeaterEntity,
    WaterHeaterEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, Platform, UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import WorltyDataCoordinator
from .worlty import WorltyBaseEntity

HVAC_MODE_MAPPING = {
    0: HVACMode.OFF,
    1: HVACMode.HEAT,
    2: HVACMode.COOL,
    3: HVACMode.AUTO,
    4: HVACMode.DRY,
    5: HVACMode.FAN_ONLY,
    6: PRESET_AWAY,
    7: PRESET_ECO,
    8: PRESET_SLEEP,
    9: PRESET_BOOST,
}


def hvac_mode_to_key(hvac_mode: str) -> int | None:
    """Convert hvac mode value to mode key."""
    for key, mode in HVAC_MODE_MAPPING.items():
        if mode == hvac_mode:
            return key
    return None


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Worlty entity."""
    coordinator: WorltyDataCoordinator = hass.data[DOMAIN][config_entry.entry_id]["api"]
    entities = []
    if coordinator.data is not None:
        entities = [
            WorltyWaterHeater(coordinator.api, entity)
            for entity in coordinator.data.get(Platform.WATER_HEATER, {}).values()
            if entity.get("hide") is not True
        ]

    async_add_entities(entities)

    @callback
    def async_add_entity(entity: dict[str, Any]):
        """Add entity from API."""
        async_add_entities([WorltyWaterHeater(coordinator.api, entity)])

    coordinator.api.register_add_listener(Platform.WATER_HEATER, async_add_entity)


class WorltyWaterHeater(WorltyBaseEntity, WaterHeaterEntity):
    """Worlty water heater."""

    _supported_features: WaterHeaterEntityFeature
    _hvac_modes: list[HVACMode]

    def __init__(self, worlty_coordinator, worlty_entity_info) -> None:
        """Initialize the entity."""
        super().__init__(worlty_coordinator, worlty_entity_info, self._update_entity)
        self._update_entity()
        self._enable_turn_on_off_backwards_compatibility = False
        self.wt_last_state: bool = self.worlty_attribute.get("stt", False)

    @callback
    def _update_entity(self) -> None:
        """Update entity."""
        self._supported_features = 0
        self._hvac_modes = [HVACMode.OFF]

        sm = self.worlty_attribute.get("sm", 0)
        for mode_bit, hvac_mode in HVAC_MODE_MAPPING.items():
            if sm & (1 << mode_bit):
                self._hvac_modes.append(hvac_mode)

        features = WaterHeaterEntityFeature.ON_OFF
        features |= WaterHeaterEntityFeature.TARGET_TEMPERATURE
        features |= WaterHeaterEntityFeature.OPERATION_MODE

        if PRESET_AWAY in self._hvac_modes:
            features |= WaterHeaterEntityFeature.AWAY_MODE

        self._supported_features = features

    @property
    def supported_features(self) -> WaterHeaterEntityFeature:
        """Return the list of supported features."""
        return self._supported_features

    @property
    def max_temp(self) -> float:
        """Max temperature."""
        return 30

    @property
    def min_temp(self) -> float:
        """Min temperature."""
        return 10

    @property
    def target_temperature_step(self) -> float | None:
        """Step temperature."""
        return self.worlty_attribute.get("ts")

    @property
    def target_temperature(self) -> float | None:
        """Target temperature."""
        return self.worlty_attribute.get("tt")

    @property
    def current_temperature(self) -> float | None:
        """Current temperature."""
        return self.worlty_attribute.get("tc")

    @property
    def temperature_unit(self) -> UnitOfTemperature:
        """Return the unit of measurement."""
        return UnitOfTemperature.CELSIUS

    @property
    def is_away_mode_on(self) -> bool:
        """Return the current status of away mode."""
        return self.worlty_attribute.get("stt", False) and hvac_mode_to_key(
            PRESET_AWAY
        ) == self.worlty_attribute.get("m", 0)

    @property
    def current_operation(self) -> str | None:
        """Return current operation ie. eco, electric, performance, ..."""
        return STATE_GAS if self.worlty_attribute.get("stt", False) else STATE_OFF

    @property
    def operation_list(self) -> list[str] | None:
        """Return current operation ie. eco, electric, performance, ..."""
        return [STATE_GAS, STATE_OFF]

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        await self.set_device(stt=True, m=1, tt=kwargs.get(ATTR_TEMPERATURE))

    async def async_turn_away_mode_on(self) -> None:
        """Turn the entity away mode on."""
        await self.set_device(stt=True, m=hvac_mode_to_key(PRESET_AWAY))

    async def async_turn_away_mode_off(self) -> None:
        """Turn the entity away mode off."""
        await self.set_device(stt=True, m=hvac_mode_to_key(HVACMode.HEAT))

    async def async_set_operation_mode(self, operation_mode: str) -> None:
        """Set new target operation mode."""
        await self.set_device(stt=operation_mode == STATE_GAS)

    async def async_turn_on(self) -> None:
        """Turn the entity on."""
        await self.set_device(stt=True)

    async def async_turn_off(self) -> None:
        """Turn the entity off."""
        await self.set_device(stt=False)
