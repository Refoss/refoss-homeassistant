"""Entity object for shared properties of refoss_lan entities."""

from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import RefossDataUpdateCoordinator
from .const import DOMAIN


class RefossEntity(CoordinatorEntity[RefossDataUpdateCoordinator]):
    """Refoss entity."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: RefossDataUpdateCoordinator, channel: int) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)

        self.coordinator = coordinator
        mac = coordinator.device.mac
        self.channel = channel
        self._attr_unique_id = f"{mac}_{channel}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, mac)},
            connections={(CONNECTION_NETWORK_MAC, mac)},
            manufacturer="Refoss",
            name=coordinator.device.device_type,
            model=coordinator.device.device_type,
            sw_version=coordinator.device.fmware_version,
            hw_version=coordinator.device.hdware_version,
        )
