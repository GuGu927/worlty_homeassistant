"""Worlty Input Number."""

from typing import Any

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import WorltyDataCoordinator
from .worlty import WorltyBaseEntity

NUMBER_RANGE = {
    "worlty_offset": [-2, 2, 0.1],
    "temp_offset": [-5, 5, 0.1],
    "temp_target": [10, 30, 0.1],
    "interval_ms": [0.5 * 60 * 60, 5 * 60 * 60, 60],
    "running_ms": [60, 60 * 60, 60],
}


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
            WorltyNumber(coordinator.api, entity)
            for entity in coordinator.data.get(Platform.NUMBER, {}).values()
            if entity.get("hide") is not True
        ]

    async_add_entities(entities)

    @callback
    def async_add_entity(entity: dict[str, Any]):
        """Add entity from API."""
        async_add_entities([WorltyNumber(coordinator.api, entity)])

    coordinator.api.register_add_listener(Platform.NUMBER, async_add_entity)


class WorltyNumber(WorltyBaseEntity, NumberEntity):
    """Worlty input number."""

    def __init__(self, worlty_coordinator, worlty_entity_info) -> None:
        """Initialize the entity."""
        super().__init__(worlty_coordinator, worlty_entity_info, self._update_entity)
        self._update_entity()

    @callback
    def _update_entity(self) -> None:
        """Update entity."""

    @property
    def native_value(self) -> float | None:
        """Return the current value of the number."""
        try:
            value = float(self.worlty_state)
            if self.worlty_name.endswith("_ms"):
                value /= 1000
            return value
        except (ValueError, TypeError):
            return None

    @property
    def native_max_value(self) -> float | None:
        """Return the maximum accepted value of the number."""
        default_range = NUMBER_RANGE.get(self.worlty_name, [0, 100, 1])
        return default_range[1]

    @property
    def native_min_value(self) -> float | None:
        """Return the maximum accepted value of the number."""
        default_range = NUMBER_RANGE.get(self.worlty_name, [0, 100, 1])
        return default_range[0]

    @property
    def native_step(self) -> float | None:
        """Return the maximum accepted value of the number."""
        default_range = NUMBER_RANGE.get(self.worlty_name, [0, 100, 1])
        return default_range[2]

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        if self.worlty_name.endswith("_ms"):
            value *= 1000
        await self.set_device(stt=value)
