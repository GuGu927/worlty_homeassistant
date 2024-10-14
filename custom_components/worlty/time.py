"""Worlty Input Time."""

from datetime import time, timedelta, datetime, timezone
from typing import Any
from homeassistant.components.time import TimeEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.sun import get_astral_event_date
from homeassistant.util import dt as dt_util
import re

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
            WorltyTime(coordinator.api, entity, hass)
            for entity in coordinator.data.get(Platform.TIME, {}).values()
            if entity.get("hide") is not True
        ]

    async_add_entities(entities)

    @callback
    def async_add_entity(entity: dict[str, Any]):
        """Add entity from API."""
        async_add_entities([WorltyTime(coordinator.api, entity, hass)])

    coordinator.api.register_add_listener(Platform.TIME, async_add_entity)


class WorltyTime(WorltyBaseEntity, TimeEntity):
    """Worlty input time."""

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
    def native_value(self) -> time | None:
        """Return the current time of the entity."""
        if self.worlty_state is None:
            return None

        tz = timezone(timedelta(hours=0))
        try:
            state = self.worlty_state
            if isinstance(state, str):
                return self._parse_special_time(state)

            hours, minutes = map(int, state.split(":"))
            return time(hour=hours, minute=minutes, timezone=tz)
        except (ValueError, TypeError):
            return None

    def _parse_special_time(self, state: str) -> time | None:
        """Parse and convert special time keywords (sunset, sunrise, etc.) with optional time adjustment."""
        tz = timezone(timedelta(hours=0))
        now = datetime.now(tz)

        match = re.match(r"^(sunset|sunrise|noon|midnight)([+-]\d{1,2}:\d{2})?$", state)
        if match:
            keyword, offset_str = match.groups()
            offset = timedelta(0)

            if offset_str:
                offset = self._parse_time_offset(offset_str)

            base_time = None
            if keyword == "sunset":
                base_time = get_astral_event_date(self.hass, "sunset", dt_util.utcnow())
            elif keyword == "sunrise":
                base_time = get_astral_event_date(
                    self.hass, "sunrise", dt_util.utcnow()
                )
            elif keyword == "noon":
                base_time = datetime.combine(now.date(), time(12, 0))
            elif keyword == "midnight":
                base_time = datetime.combine(now.date(), time(0, 0))

            if base_time:
                adjusted_time = (base_time + offset).time()
                return adjusted_time
        return None

    def _parse_time_offset(self, offset_str: str) -> timedelta:
        """Convert a string offset in the format +-HH:MM to a timedelta object."""
        sign = 1 if "+" in offset_str else -1
        hours, minutes = map(int, offset_str[1:].split(":"))
        return timedelta(hours=hours, minutes=minutes) * sign

    async def async_set_value(self, value: time) -> None:
        """Update the time."""
        time_string = time.strftime("%H:%M", value)
        await self.set_device(stt=time_string)
