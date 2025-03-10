"""Support for refoss_lan sensors."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from .const import CHANNEL_DISPLAY_NAME, SENSOR_EM
from .entity import RefossEntity
from .refoss_ha.controller.electricity import ElectricityXMix
from .coordinator import RefossDataUpdateCoordinator, RefossConfigEntry


@dataclass(frozen=True)
class RefossSensorEntityDescription(SensorEntityDescription):
    """Describes Refoss sensor entity."""

    subkey: str | None = None
    fn: Callable[[float], float] | None = None


DEVICETYPE_SENSOR: dict[str, str] = {
    "em06": SENSOR_EM,
    "em16": SENSOR_EM,
}

SENSORS: dict[str, tuple[RefossSensorEntityDescription, ...]] = {
    SENSOR_EM: (
        RefossSensorEntityDescription(
            key="power",
            translation_key="power",
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfPower.WATT,
            suggested_display_precision=2,
            subkey="power",
            fn=lambda x: x / 1000.0,
        ),
        RefossSensorEntityDescription(
            key="voltage",
            translation_key="voltage",
            device_class=SensorDeviceClass.VOLTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfElectricPotential.MILLIVOLT,
            suggested_display_precision=2,
            suggested_unit_of_measurement=UnitOfElectricPotential.VOLT,
            subkey="voltage",
        ),
        RefossSensorEntityDescription(
            key="current",
            translation_key="current",
            device_class=SensorDeviceClass.CURRENT,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfElectricCurrent.MILLIAMPERE,
            suggested_display_precision=2,
            suggested_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
            subkey="current",
        ),
        RefossSensorEntityDescription(
            key="factor",
            translation_key="power_factor",
            device_class=SensorDeviceClass.POWER_FACTOR,
            state_class=SensorStateClass.MEASUREMENT,
            suggested_display_precision=2,
            subkey="factor",
        ),
        RefossSensorEntityDescription(
            key="energy",
            translation_key="this_month_energy",
            device_class=SensorDeviceClass.ENERGY,
            state_class=SensorStateClass.TOTAL_INCREASING,
            native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
            suggested_display_precision=2,
            subkey="mConsume",
            fn=lambda x: max(0, x),
        ),
        RefossSensorEntityDescription(
            key="energy_returned",
            translation_key="this_month_energy_returned",
            device_class=SensorDeviceClass.ENERGY,
            state_class=SensorStateClass.TOTAL_INCREASING,
            native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
            suggested_display_precision=2,
            subkey="mConsume",
            fn=lambda x: abs(x) if x < 0 else 0,
        ),
    ),
}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: RefossConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Refoss device from a config entry."""
    coordinator = config_entry.runtime_data
    device = coordinator.device
    if not isinstance(device, ElectricityXMix):
        return

    def init_device(device: ElectricityXMix):
        """Register the device."""
        sensor_type = DEVICETYPE_SENSOR.get(device.device_type, "")
        descriptions: tuple[RefossSensorEntityDescription, ...] = SENSORS.get(
            sensor_type, ()
        )
        async_add_entities(
            RefossSensor(
                coordinator=coordinator,
                channel=channel,
                description=description,
            )
            for channel in device.channels
            for description in descriptions
        )

    init_device(device)


class RefossSensor(RefossEntity, SensorEntity):
    """Refoss Sensor Device."""

    entity_description: RefossSensorEntityDescription

    def __init__(
        self,
        coordinator: RefossDataUpdateCoordinator,
        channel: int,
        description: RefossSensorEntityDescription,
    ) -> None:
        """Init Refoss sensor."""
        super().__init__(coordinator, channel)
        self.entity_description = description
        self._attr_unique_id = f"{super().unique_id}{description.key}"
        device_type = coordinator.device.device_type
        channel_name = CHANNEL_DISPLAY_NAME[device_type][channel]
        self._attr_translation_placeholders = {"channel_name": channel_name}

    @property
    def native_value(self) -> StateType:
        """Return the native value."""
        value = self.coordinator.device.get_value(
            self.channel, self.entity_description.subkey
        )
        if value is None:
            return None
        if self.entity_description.fn:
            return self.entity_description.fn(value)
        return value
