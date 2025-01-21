"""Config Flow for refoss_lan integration."""

from __future__ import annotations

from __future__ import annotations
import voluptuous as vol

from typing import Any, Final
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

from homeassistant.const import (
    CONF_HOST,
    CONF_MAC,
)
from .refoss_ha.discovery import Discovery
from .refoss_ha.exceptions import SocketError
from .const import _LOGGER

CONFIG_SCHEMA: Final = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
    }
)

from .const import DISCOVERY_TIMEOUT, DOMAIN


class RefossConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for refoss_lan."""

    VERSION = 1
    MINOR_VERSION = 1

    host: str = ""

    async def async_step_user(
            self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            host = user_input[CONF_HOST]
            device = await start_scan_device(host=host)
            if not device:
                errors["base"] = "no_devices_found"
            else:
                if mac := device[CONF_MAC]:
                    await self.async_set_unique_id(mac)
                    self._abort_if_unique_id_configured({CONF_HOST: host})
                    return self.async_create_entry(
                        title=device["devName"],
                        data={CONF_HOST: host, "device": device},
                    )
                errors["base"] = "firmware_not_fully_supported"
        return self.async_show_form(
            step_id="user", data_schema=CONFIG_SCHEMA, errors=errors
        )

    async def async_step_reconfigure(
            self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a reconfiguration flow initialized by the user."""
        errors = {}
        reconfigure_entry = self._get_reconfigure_entry()
        self.host = reconfigure_entry.data[CONF_HOST]
        if user_input is not None:
            host = user_input[CONF_HOST]

            device = await start_scan_device(host=host)
            if not device:
                errors["base"] = "no_devices_found"
            else:
                if mac := device[CONF_MAC]:
                    await self.async_set_unique_id(mac)
                    self._abort_if_unique_id_mismatch(reason="another_device")

                    return self.async_update_reload_and_abort(
                        reconfigure_entry,
                        data_updates={CONF_HOST: host, "device": device},
                    )
                errors["base"] = "firmware_not_fully_supported"
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema({vol.Required(CONF_HOST, default=self.host): str}),
            description_placeholders={"device_name": reconfigure_entry.title},
            errors=errors,
        )


async def start_scan_device(host: str) -> dict | None:
    """Scan device on the host."""
    device = None
    discovery_server = Discovery()
    try:
        await discovery_server.initialize()
        device = await discovery_server.broadcast_msg(
            ip=host, wait_for=DISCOVERY_TIMEOUT
        )
    except SocketError:
        _LOGGER.debug(f"Failed socket scan on {host}")
    finally:
        discovery_server.closeDiscovery()
        return device
