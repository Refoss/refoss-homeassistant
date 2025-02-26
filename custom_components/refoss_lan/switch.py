"""Switch for refoss_lan."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import RefossEntity
from .refoss_ha.controller.toggle import ToggleXMix
from .coordinator import RefossDataUpdateCoordinator, RefossConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: RefossConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Refoss device from a config entry."""
    coordinator = config_entry.runtime_data
    device = coordinator.device

    if not isinstance(device, ToggleXMix):
        return

    def init_device(device: ToggleXMix):
        """Register the device."""
        new_entities = []
        for channel in device.channels:
            entity = RefossSwitch(coordinator=coordinator, channel=channel)
            new_entities.append(entity)

        async_add_entities(new_entities)

    init_device(device)


class RefossSwitch(RefossEntity, SwitchEntity):
    """Refoss Switch Device."""

    def __init__(
        self,
        coordinator: RefossDataUpdateCoordinator,
        channel: int,
    ) -> None:
        """Init Refoss switch."""
        super().__init__(coordinator, channel)
        self._attr_name = str(channel)

    @property
    def is_on(self) -> bool | None:
        """Return true if switch is on."""
        return self.coordinator.device.is_on(channel=self.channel)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        await self.coordinator.device.async_turn_on(self.channel)
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        await self.coordinator.device.async_turn_off(self.channel)
        self.async_write_ha_state()

    async def async_toggle(self, **kwargs: Any) -> None:
        """Toggle the switch."""
        await self.coordinator.device.async_toggle(channel=self.channel)
        self.async_write_ha_state()
