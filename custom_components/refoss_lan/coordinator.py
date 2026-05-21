"""Helper and coordinator for refoss_lan."""

from __future__ import annotations

from datetime import timedelta

from .refoss_ha.controller.device import BaseDevice
from .refoss_ha.exceptions import DeviceTimeoutError, RefossError

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import _LOGGER, DOMAIN, UPDATE_INTERVAL

type RefossConfigEntry = ConfigEntry[RefossDataUpdateCoordinator]


class RefossDataUpdateCoordinator(DataUpdateCoordinator[None]):
    """Manages polling for state changes from the device."""

    config_entry: ConfigEntry

    def __init__(
        self, hass: HomeAssistant, config_entry: ConfigEntry, device: BaseDevice
    ) -> None:
        """Initialize the data update coordinator."""
        update_interval = config_entry.data.get(UPDATE_INTERVAL, 10)
        super().__init__(
            hass,
            _LOGGER,
            config_entry=config_entry,
            name=f"{DOMAIN}-{device.device_info.dev_name}",
            update_interval=timedelta(seconds=update_interval),
        )
        self.device = device

    async def _async_update_data(self) -> None:
        """Update the state of the device."""
        try:
            await self.device.async_handle_update()
        except DeviceTimeoutError as e:
            _LOGGER.debug("Device update timed out: %s", self.device.dev_name)
            raise UpdateFailed("Timeout") from e
        except RefossError as e:
            _LOGGER.debug("Device connection error for %s: %s", self.device.dev_name, e)
            raise UpdateFailed("Device connect fail") from e
