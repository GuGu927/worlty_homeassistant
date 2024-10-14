"""Worlty Input Date."""

from datetime import date, datetime, timedelta, timezone
from typing import Any
from homeassistant.components.date import DateEntity
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
    coordinator: WorltyDataCoordinator = hass.data[DOMAIN][config_entry.entry_id]["api"]
    entities = []
    if coordinator.data is not None:
        entities = [
            WorltyDate(coordinator.api, entity, hass)
            for entity in coordinator.data.get(Platform.DATE, {}).values()
            if entity.get("hide") is not True
        ]

    async_add_entities(entities)

    @callback
    def async_add_entity(entity: dict[str, Any]):
        """Add entity from API."""
        async_add_entities([WorltyDate(coordinator.api, entity, hass)])

    coordinator.api.register_add_listener(Platform.DATE, async_add_entity)


class WorltyDate(WorltyBaseEntity, DateEntity):
    """Worlty input date."""

    def __init__(
        self, worlty_coordinator, worlty_entity_info, hass: HomeAssistant
    ) -> None:
        """Initialize the entity."""
        self.hass = hass
        super().__init__(worlty_coordinator, worlty_entity_info, self._update_entity)
        self._update_entity()

    @callback
    def _update_entity(self) -> None:
        """Update entity."""

    @property
    def native_value(self) -> date | None:
        """Return the current date of the entity."""
        if self.worlty_state is None:
            return None

        tz = timezone(timedelta(hours=9))
        try:
            state = self.worlty_state
            if isinstance(state, str):
                return datetime.strptime(state, "%m/%d").date(timezone=tz)

            return date.today(timezone=tz)
        except (ValueError, TypeError):
            return None

    async def async_set_value(self, value: date) -> None:
        """Update the date."""
        date_string = value.strftime("%m/%d")
        await self.set_device(stt=date_string)
