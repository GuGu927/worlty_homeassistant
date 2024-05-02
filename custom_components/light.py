"""Worlty light."""

import math
from typing import Any

from homeassistant.components.light import ATTR_BRIGHTNESS, ColorMode, LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.color import value_to_brightness
from homeassistant.util.percentage import percentage_to_ranged_value

from .const import DOMAIN
from .coordinator import WorltyDataCoordinator
from .worlty import WorltyBaseEntity


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
            WorltyLight(coordinator.api, entity)
            for entity in coordinator.data.get(Platform.LIGHT, {}).values()
            if entity.get("hide") is not True
        ]

    async_add_entities(entities)

    @callback
    def async_add_entity(entity: dict[str, Any]):
        """Add entity from API."""
        async_add_entities([WorltyLight(coordinator.api, entity)])

    coordinator.api.register_add_listener(Platform.LIGHT, async_add_entity)


class WorltyLight(WorltyBaseEntity, LightEntity):
    """Worlty light."""

    def __init__(self, worlty_coordinator, worlty_entity_info) -> None:
        """Initialize the entity."""
        super().__init__(worlty_coordinator, worlty_entity_info, self._update_entity)
        self._update_entity()
        self._color_mode: ColorMode = ColorMode.ONOFF
        self.wt_last_bri: int = 0
        self.wt_level_max: int = 0

    @callback
    def _update_entity(self) -> None:
        """Update entity."""

    @property
    def is_on(self) -> bool:
        """Return true if entity is on."""
        return self.worlty_attribute.get("stt", False)

    @property
    def brightness(self) -> int | None:
        """Return the current brightness."""
        bri = self.worlty_attribute.get("bri")

        self.wt_level_max = self.worlty_attribute.get("lvm")
        level = self.worlty_attribute.get("lv", 0)
        if level > 0 and self.wt_level_max >= level:
            bri = value_to_brightness((1, self.wt_level_max), level)
        if bri is not None and bri > 0:
            self.wt_last_bri = bri
        return bri

    @property
    def color_mode(self) -> ColorMode:
        """Return the color mode."""
        return self._color_mode

    @property
    def supported_color_modes(self) -> set[ColorMode]:
        """Return the list of supported color mode."""
        modes = [ColorMode.ONOFF]
        sc = self.worlty_attribute.get("sc", 0)
        if (sc & (1 << 2)) != 0:
            modes.append(ColorMode.BRIGHTNESS)
        return modes

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        if self.wt_level_max > 1:
            value_in_range = math.ceil(
                percentage_to_ranged_value(
                    (1, self.wt_level_max), kwargs[ATTR_BRIGHTNESS]
                )
            )
            await self.set_device(stt=True, bri=value_in_range)
        else:
            await self.set_device(stt=True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        await self.set_device(stt=False)
