"""Worlty sensor."""

from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

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
            WorltySensor(coordinator.api, entity)
            for entity in coordinator.data.get(Platform.SENSOR, {}).values()
            if entity.get("hide") is not True
        ]

    async_add_entities(entities)

    @callback
    def async_add_entity(entity: dict[str, Any]):
        """Add entity from API."""
        async_add_entities([WorltySensor(coordinator.api, entity)])

    coordinator.api.register_add_listener(Platform.SENSOR, async_add_entity)


class WorltySensor(WorltyBaseEntity, SensorEntity):
    """Worlty sensor."""

    def __init__(self, worlty_coordinator, worlty_entity_info) -> None:
        """Initialize the entity."""
        super().__init__(worlty_coordinator, worlty_entity_info, self._update_entity)
        self._update_entity()

    @callback
    def _update_entity(self) -> None:
        """Update entity."""

    @property
    def native_value(self) -> StateType:
        """Return the native value of the sensor."""
        return self.worlty_state

    @property
    def state_class(self) -> SensorStateClass | None:
        """Type of this sensor state."""
        if self.worlty_name in ["usage"]:
            return SensorStateClass.MEASUREMENT
        return None
