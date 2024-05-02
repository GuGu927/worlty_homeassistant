"""Config flow for Worlty."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components import onboarding, zeroconf
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_ACCESS_TOKEN, CONF_HOST, CONF_IP_ADDRESS, CONF_PORT
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, LOGGER, MANUFACTURER
from .worlty import WorltyLocal


class WorltyFlowHandler(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Worlty."""

    VERSION = 1

    _device: list[str, int]

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a flow initialized by the user."""
        errors = {}
        if user_input:
            api = WorltyLocal(
                self.hass,
                user_input.get(CONF_IP_ADDRESS),
                user_input.get(CONF_PORT),
                user_input.get(CONF_ACCESS_TOKEN),
                None,
            )
            auth, message = await api.auth(None)
            if auth is True:
                api.terminate()
                await self.async_set_unique_id(message.get("device_id"))
                self._abort_if_unique_id_configured(
                    updates={
                        CONF_IP_ADDRESS: user_input.get(CONF_IP_ADDRESS),
                        CONF_PORT: user_input.get(CONF_PORT),
                    }
                )
                return self.async_create_entry(
                    title=message.get("device_id", MANUFACTURER), data=user_input
                )
            if message == "invalid_access_token":
                errors = {CONF_ACCESS_TOKEN: message}
            elif message == "cannot_connect":
                errors = {CONF_IP_ADDRESS: message, CONF_PORT: message}
            elif message == "unreachable":
                self.async_abort(reason="no_devices_found")

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_IP_ADDRESS): cv.string,
                    vol.Required(CONF_PORT): cv.port,
                    vol.Required(CONF_ACCESS_TOKEN): cv.string,
                }
            ),
            errors=errors,
        )

    async def async_step_zeroconf(
        self, discovery_info: zeroconf.ZeroconfServiceInfo
    ) -> ConfigFlowResult:
        """Handle zeroconf discovery."""

        host = discovery_info.host
        port = discovery_info.port
        if port != 80:
            device_id = discovery_info.name.split(".")[0]
            await self.async_set_unique_id(device_id)
            self._abort_if_unique_id_configured()

            LOGGER.info(f"Device found with {device_id} [{host}:{port}]")
            self._device = [device_id, host, port]
            return await self.async_step_discovery_confirm()
        return self.async_abort(reason="unreachable")

    async def async_step_discovery_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm discovery."""
        if user_input is not None or not onboarding.async_is_onboarded(self.hass):
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required(
                            CONF_IP_ADDRESS, default=self._device[1]
                        ): cv.string,
                        vol.Required(CONF_PORT, default=self._device[2]): cv.port,
                        vol.Required(CONF_ACCESS_TOKEN): cv.string,
                    }
                ),
                errors={},
            )

        placeholders = {
            CONF_HOST: self._device[0],
            CONF_IP_ADDRESS: self._device[1],
            CONF_PORT: self._device[2],
        }
        return self.async_show_form(
            step_id="discovery_confirm",
            description_placeholders=placeholders,
        )
