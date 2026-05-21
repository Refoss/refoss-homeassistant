"""The refoss_lan integration."""

from __future__ import annotations

from typing import Final

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform, CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .refoss_ha.device_manager import async_build_base_device
from .refoss_ha.device import DeviceInfo
from .refoss_ha.exceptions import DeviceTimeoutError, InvalidMessage, RefossError

from .refoss_ha.controller.device import BaseDevice
from .const import DOMAIN, _LOGGER
from .coordinator import RefossDataUpdateCoordinator, RefossConfigEntry

PLATFORMS: Final = [
    Platform.SWITCH,
    Platform.SENSOR,
]


async def async_setup_entry(
    hass: HomeAssistant, config_entry: RefossConfigEntry
) -> bool:
    """Set up refoss_lan from a config entry."""
    data = config_entry.data
    if not data.get(CONF_HOST) or not data.get("device"):
        _LOGGER.debug(
            "The config entry %s invalid, please remove it and try again",
            config_entry.title,
        )
        return False
    try:
        device: DeviceInfo = DeviceInfo.from_dict(data["device"])
        device.set_session(async_get_clientsession(hass))
        base_device: BaseDevice = await async_build_base_device(device_info=device)
    except DeviceTimeoutError as err:
        _LOGGER.debug("Device timeout during setup for %s: %s", data[CONF_HOST], err)
        raise ConfigEntryNotReady(f"Timed out connecting to {data[CONF_HOST]}") from err
    except InvalidMessage as err:
        _LOGGER.debug("Invalid message from device %s: %s", data[CONF_HOST], err)
        raise ConfigEntryNotReady(f"Device data error {data[CONF_HOST]}") from err
    except RefossError as err:
        _LOGGER.debug(
            "Device %s network connection failed: %s", config_entry.title, err,
        )
        raise ConfigEntryNotReady(repr(err)) from err

    coordinator = RefossDataUpdateCoordinator(hass, config_entry, base_device)
    await coordinator.async_config_entry_first_refresh()
    config_entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    return True


async def async_unload_entry(
    hass: HomeAssistant, config_entry: RefossConfigEntry
) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        config_entry, PLATFORMS
    )
    return unload_ok


async def async_migrate_entry(
    hass: HomeAssistant, config_entry: ConfigEntry
) -> bool:
    """Migrate old entry data to new version."""
    _LOGGER.debug(
        "Migrating from version %s.%s", config_entry.version, config_entry.minor_version
    )

    if config_entry.version == 1 and config_entry.minor_version == 1:
        # Current version — no migration needed.
        # Future migrations should be added here, e.g.:
        # if config_entry.minor_version < 2:
        #     new_data = {**config_entry.data, "new_field": "default"}
        #     hass.config_entries.async_update_entry(
        #         config_entry, data=new_data, minor_version=2
        #     )
        return True

    _LOGGER.error(
        "Migration from version %s.%s is not supported",
        config_entry.version,
        config_entry.minor_version,
    )
    return False
