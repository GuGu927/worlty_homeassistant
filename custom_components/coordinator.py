"""DataUpdateCoordinators for worlty integration."""

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ACCESS_TOKEN, CONF_IP_ADDRESS, CONF_PORT, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, LOGGER
from .worlty import WorltyLocal


class WorltyDataCoordinator(DataUpdateCoordinator):
    """Define a wrapper class to update Worlty data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Set up the WorltyDataCoordinator class."""
        self.hass = hass
        self.entry = entry
        self.api: WorltyLocal

        super().__init__(hass, LOGGER, name=DOMAIN)

    async def connect(self):
        """Wolrty API create."""
        self.api = await WorltyLocal.create(
            self.hass,
            self.entry.data.get(CONF_IP_ADDRESS),
            self.entry.data.get(CONF_PORT),
            self.entry.data.get(CONF_ACCESS_TOKEN),
            self.async_event_handler,
        )

    async def _async_update_data(self) -> dict[Platform, dict[str, dict[str, Any]]]:
        """Update Worlty devices data."""
        try:
            return await self.api.get_worlty_devices()
        except Exception as err:
            raise UpdateFailed(err) from err

    async def async_event_handler(self, event, data):
        """Worlty event handler."""
        self.async_update_listeners()
