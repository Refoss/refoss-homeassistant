"""The refoss_lan integration."""

from __future__ import annotations

from typing import Final

from homeassistant.const import Platform, CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

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
        base_device: BaseDevice = await async_build_base_device(device_info=device)
    except DeviceTimeoutError as err:
        raise ConfigEntryNotReady(f"Timed out connecting to {data[CONF_HOST]}") from err
    except InvalidMessage as err:
        raise ConfigEntryNotReady(f"Device data error {data[CONF_HOST]}") from err
    except RefossError as err:
        _LOGGER.debug(
            f"Device {config_entry.title} network connection failed, please check the network and try again"
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
