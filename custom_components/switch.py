"""Worlty switch."""

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

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
            WorltySwitch(coordinator.api, entity)
            for entity in coordinator.data.get(Platform.SWITCH, {}).values()
            if entity.get("hide") is not True
        ]

    async_add_entities(entities)

    @callback
    def async_add_entity(entity: dict[str, Any]):
        """Add entity from API."""
        async_add_entities([WorltySwitch(coordinator.api, entity)])

    coordinator.api.register_add_listener(Platform.SWITCH, async_add_entity)


class WorltySwitch(WorltyBaseEntity, SwitchEntity):
    """Worlty switch."""

    def __init__(self, worlty_coordinator, worlty_entity_info) -> None:
        """Initialize the entity."""
        super().__init__(worlty_coordinator, worlty_entity_info, self._update_entity)
        self._update_entity()

    @callback
    def _update_entity(self) -> None:
        """Update entity."""

    @property
    def is_on(self) -> bool:
        """Return true if entity is on."""
        return self.worlty_attribute.get("stt", False)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        await self.set_device(stt=True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        await self.set_device(stt=False)
