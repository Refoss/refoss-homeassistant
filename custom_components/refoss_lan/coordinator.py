"""Helper and coordinator for refoss_lan."""

from __future__ import annotations

from datetime import timedelta

from .refoss_ha.controller.device import BaseDevice
from .refoss_ha.exceptions import DeviceTimeoutError, RefossError

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import _LOGGER, DOMAIN, MAX_ERRORS, UPDATE_INTERVAL

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
        self._error_count = 0

    async def _async_update_data(self) -> None:
        """Update the state of the device."""
        try:
            await self.device.async_handle_update()
            self._update_success(True)
        except DeviceTimeoutError as e:
            self._update_error_count()
            if self._error_count >= MAX_ERRORS:
                self._update_success(False)
            _LOGGER.debug("Device update timed out")
            raise UpdateFailed("Timeout") from e
        except RefossError as e:
            _LOGGER.debug(f"Device connection error: {e!r}")
            raise UpdateFailed("Device connect fail") from e

    def _update_success(self, success: bool) -> None:
        """Update the success state."""
        self.last_update_success = success
        self._error_count = 0 if success else self._error_count

    def _update_error_count(self) -> None:
        """Increment the error count."""
        self._error_count += 1
