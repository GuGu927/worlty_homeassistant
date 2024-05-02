"""The Worlty integration."""

from __future__ import annotations

import asyncio

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import WorltyDataCoordinator

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.CLIMATE,
    Platform.FAN,
    Platform.LIGHT,
    Platform.SENSOR,
    Platform.SWITCH,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Worlty from a config entry."""

    async def init_coordinator(coordinator: WorltyDataCoordinator):
        """Initialize coordinator."""
        if entry.unique_id is None:
            hass.config_entries.async_update_entry(
                entry, unique_id=coordinator.api.worlty_pad.mac_address
            )

        await coordinator.async_config_entry_first_refresh()

        hass.data[DOMAIN]["task"] = hass.loop.create_task(
            coordinator.api.listen_for_message()
        )

    async def retry_auth(coordinator: WorltyDataCoordinator):
        """Retry auth."""
        auth = False
        auth_count = 0
        while not auth and auth_count <= 10:
            auth_count += 1
            auth, _ = await coordinator.api.auth(entry)
            if auth is False:
                await asyncio.sleep(5)
            else:
                await init_coordinator(coordinator)

    coordinator: WorltyDataCoordinator = WorltyDataCoordinator(hass, entry)
    await coordinator.connect()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    if coordinator.api is not None:
        auth, _ = await coordinator.api.auth(entry)

        if auth is True:
            await init_coordinator(coordinator)
        else:
            hass.loop.create_task(retry_auth(coordinator))

        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        coordinator: WorltyDataCoordinator = hass.data[DOMAIN][entry.entry_id]
        await coordinator.api.disconnect()
        task = hass.data[DOMAIN]["task"]
        task.cancel()
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
