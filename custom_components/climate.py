"""Worlty climate."""

from typing import Any

from homeassistant.components.climate import (
    FAN_AUTO,
    FAN_DIFFUSE,
    FAN_FOCUS,
    FAN_HIGH,
    FAN_LOW,
    FAN_MEDIUM,
    FAN_OFF,
    FAN_ON,
    PRESET_AWAY,
    PRESET_BOOST,
    PRESET_ECO,
    PRESET_NONE,
    PRESET_SLEEP,
    SWING_BOTH,
    SWING_HORIZONTAL,
    SWING_OFF,
    SWING_ON,
    SWING_VERTICAL,
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
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
}


FAN_MODE_MAPPING = {
    0: FAN_OFF,
    1: FAN_ON,
    2: FAN_AUTO,
    3: FAN_LOW,
    4: FAN_MEDIUM,
    5: FAN_HIGH,
    6: FAN_FOCUS,
    7: FAN_DIFFUSE,
    8: "natural",
    9: "weak",
    10: "turbo",
}

PRESET_MODE_MAPPING = {
    6: PRESET_AWAY,
    7: PRESET_ECO,
    8: PRESET_SLEEP,
    9: PRESET_BOOST,
}

SWING_MODE_MAPPING = {
    0: SWING_OFF,
    1: SWING_ON,
    2: SWING_VERTICAL,
    3: SWING_HORIZONTAL,
    4: SWING_BOTH,
}

CLIMATE_ACTION_MAPPING = {
    0: HVACAction.OFF,
    1: HVACAction.HEATING,
    2: HVACAction.COOLING,
    4: HVACAction.DRYING,
    5: HVACAction.FAN,
    10: HVACAction.IDLE,
}


def hvac_mode_to_key(hvac_mode: HVACMode) -> int | None:
    """Convert hvac mode value to mode key."""
    for key, mode in HVAC_MODE_MAPPING.items():
        if mode == hvac_mode:
            return key
    return None


def fan_mode_to_key(fan_mode: str) -> int | None:
    """Convert fan mode value to mode key."""
    for key, mode in FAN_MODE_MAPPING.items():
        if mode == fan_mode:
            return key
    return None


def preset_mode_to_key(preset_mode: str) -> int | None:
    """Convert preset mode value to mode key."""
    for key, mode in PRESET_MODE_MAPPING.items():
        if mode == preset_mode:
            return key
    return None


def swing_mode_to_key(swing_mode: str) -> int | None:
    """Convert swing mode value to mode key."""
    for key, mode in SWING_MODE_MAPPING.items():
        if mode == swing_mode:
            return key
    return None


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Worlty entity."""
    coordinator: WorltyDataCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    entities = []
    if coordinator.data is not None:
        entities = [
            WorltyClimate(coordinator.api, entity)
            for entity in coordinator.data.get(Platform.CLIMATE, {}).values()
            if entity.get("hide") is not True
        ]

    async_add_entities(entities)

    @callback
    def async_add_entity(entity: dict[str, Any]):
        """Add entity from API."""
        async_add_entities([WorltyClimate(coordinator.api, entity)])

    coordinator.api.register_add_listener(Platform.CLIMATE, async_add_entity)


class WorltyClimate(WorltyBaseEntity, ClimateEntity):
    """Worlty climate."""

    _supported_features: ClimateEntityFeature
    _hvac_modes: list[HVACMode]
    _preset_modes: list[str]
    _fan_modes: list[str]
    _swing_modes: list[str]

    def __init__(self, worlty_coordinator, worlty_entity_info) -> None:
        """Initialize the entity."""
        super().__init__(worlty_coordinator, worlty_entity_info, self._update_entity)
        self._update_entity()
        self._enable_turn_on_off_backwards_compatibility = False
        self.wt_last_state: bool = self.worlty_attribute.get("stt", False)
        self.wt_last_mode: HVACMode = self.worlty_attribute.get("m", HVACMode.OFF)
        self.wt_last_fan: str = self.worlty_attribute.get("f", FAN_OFF)
        self.wt_last_swing: str = self.worlty_attribute.get("a", SWING_OFF)
        self.wt_last_preset: str = self.preset_mode

    @callback
    def _update_entity(self) -> None:
        """Update entity."""
        self._supported_features = 0
        self._hvac_modes = [HVACMode.OFF]
        self._preset_modes = []
        self._fan_modes = []
        self._swing_modes = []

        sm = self.worlty_attribute.get("sm", 0)
        self._hvac_modes = [HVACMode.OFF]

        for mode_bit, hvac_mode in HVAC_MODE_MAPPING.items():
            if sm & (1 << mode_bit):
                self._hvac_modes.append(hvac_mode)

        self._preset_modes = [PRESET_NONE]

        for preset_bit, preset_mode in PRESET_MODE_MAPPING.items():
            if sm & (1 << preset_bit):
                self._preset_modes.append(preset_mode)

        sf = self.worlty_attribute.get("sf", 0)
        self._fan_modes = []

        for fan_bit, fan_mode in FAN_MODE_MAPPING.items():
            if sf & (1 << fan_bit):
                self._fan_modes.append(fan_mode)

        ssw = self.worlty_attribute.get("ssw", 0)
        self._swing_modes = []

        for swing_bit, swing_mode in SWING_MODE_MAPPING.items():
            if ssw & (1 << swing_bit):
                self._swing_modes.append(swing_mode)

        tt, tc = self.target_temperature, self.current_temperature
        ht, hc = self.target_humidity, self.current_humidity

        features = ClimateEntityFeature.TURN_ON
        features |= ClimateEntityFeature.TURN_OFF
        if tt is not None or tc is not None:
            features |= ClimateEntityFeature.TARGET_TEMPERATURE
        if ht is not None or hc is not None:
            features |= ClimateEntityFeature.TARGET_HUMIDITY
        if len(self._preset_modes) > 1:
            features |= ClimateEntityFeature.PRESET_MODE
        if len(self._fan_modes) > 0:
            features |= ClimateEntityFeature.FAN_MODE
        if len(self._swing_modes) > 0:
            features |= ClimateEntityFeature.SWING_MODE
        self._supported_features = features

    @property
    def hvac_action(self) -> HVACAction:
        """Return hvac action."""
        action = self.worlty_attribute.get("a")
        state = self.worlty_attribute.get("stt", False)
        if action is None:
            return None
        return (
            CLIMATE_ACTION_MAPPING.get(action, HVACAction.IDLE)
            if state
            else HVACAction.OFF
        )

    @property
    def hvac_mode(self) -> HVACMode:
        """Return hvac operation ie. heat, cool mode."""
        mode = self.worlty_attribute.get("m")
        state = self.worlty_attribute.get("stt", False)
        self.wt_last_state = state
        if self.wt_last_state:
            self.wt_last_mode = HVAC_MODE_MAPPING.get(mode, HVACMode.OFF)
            return self.wt_last_mode
        return HVACMode.OFF

    @property
    def hvac_modes(self) -> list[HVACMode]:
        """Return the list of available hvac operation modes."""
        return self._hvac_modes

    @property
    def preset_mode(self) -> str | None:
        """Return hvac preset mode."""
        mode = self.worlty_attribute.get("m", 0)
        return PRESET_MODE_MAPPING.get(mode, PRESET_NONE)

    @property
    def preset_modes(self) -> list[str]:
        """Return the list of available hvac preset modes."""
        return self._preset_modes

    @property
    def fan_mode(self) -> str | None:
        """Return the hvac fan mode."""
        fan = self.worlty_attribute.get("f", 0)
        fan_mode = FAN_MODE_MAPPING.get(fan, FAN_OFF)
        if self.wt_last_state:
            self.wt_last_fan = fan_mode
        return fan_mode

    @property
    def fan_modes(self) -> list[str]:
        """Return the list of available hvac fan modes."""
        return self._fan_modes

    @property
    def swing_mode(self) -> str | None:
        """Return the hvac swing mode."""
        swing = self.worlty_attribute.get("sw", 0)
        swing_mode = SWING_MODE_MAPPING.get(swing, SWING_OFF)
        if self.wt_last_state:
            self.wt_last_swing = swing_mode
        return swing_mode

    @property
    def swing_modes(self) -> list[str]:
        """Return the list of available hvac swing modes."""
        return self._swing_modes

    @property
    def supported_features(self) -> ClimateEntityFeature:
        """Return the list of supported features."""
        return self._supported_features

    @property
    def temperature_unit(self) -> UnitOfTemperature:
        """Return the unit of measurement."""
        return UnitOfTemperature.CELSIUS

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
    def target_humidity(self) -> float | None:
        """Step humidity."""
        return self.worlty_attribute.get("ht")

    @property
    def current_humidity(self) -> float | None:
        """Current humidity."""
        return self.worlty_attribute.get("hc")

    async def async_turn_on(self) -> None:
        """Turn the entity on."""
        await self.set_device(stt=True)

    async def async_turn_off(self) -> None:
        """Turn the entity off."""
        await self.set_device(stt=False)

    async def async_toggle(self) -> None:
        """Toggle the entity."""
        await self.set_device(stt=not self.wt_last_state)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new target hvac mode."""
        if hvac_mode == HVACMode.OFF:
            await self.async_turn_off()
            return None
        await self.set_device(stt=True, m=hvac_mode_to_key(hvac_mode))

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set new target preset mode."""
        hvac_mode = None
        if preset_mode == PRESET_AWAY:
            hvac_mode = preset_mode_to_key(PRESET_AWAY)
        elif preset_mode == PRESET_NONE:
            hvac_mode = hvac_mode_to_key(HVACMode.HEAT)
        if hvac_mode is None:
            return None
        await self.set_device(stt=True, m=hvac_mode)

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set new target fan mode."""
        if self.hvac_mode == HVACMode.AUTO:
            return None
        await self.set_device(stt=True, f=fan_mode_to_key(fan_mode))

    async def async_set_swing_mode(self, swing_mode: str) -> None:
        """Set new target swing operation."""
        await self.set_device(stt=True, sw=swing_mode_to_key(swing_mode))

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        if self.hvac_mode == HVACMode.FAN_ONLY:
            return None
        await self.set_device(stt=True, tt=kwargs.get(ATTR_TEMPERATURE))

    async def async_set_humidity(self, humidity: int) -> None:
        """Set new target humidity."""
        if self.hvac_mode == HVACMode.FAN_ONLY:
            return None
        await self.set_device(stt=True, ht=humidity)
