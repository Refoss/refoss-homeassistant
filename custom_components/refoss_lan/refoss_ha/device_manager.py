"""device_manager."""
from __future__ import annotations

from functools import lru_cache
from typing import Optional

from .controller.device import BaseDevice
from .controller.toggle import ToggleXMix
from .controller.electricity import ElectricityXMix
from .enums import Namespace
from .device import DeviceInfo
from .exceptions import InvalidMessage

_ABILITY_MATRIX = {
    Namespace.CONTROL_TOGGLEX.value: ToggleXMix,
    Namespace.CONTROL_ELECTRICITYX.value: ElectricityXMix,
}


async def async_build_base_device(device_info: DeviceInfo) -> Optional[BaseDevice]:
    """Build base device."""
    res = await device_info.async_execute_cmd(
        device_uuid=device_info.uuid,
        method="GET",
        namespace=Namespace.SYSTEM_ABILITY,
        payload={},
    )
    if res is None:
        raise InvalidMessage("%s get ability failed", device_info.dev_name)

    abilities = res.get("payload", {}).get("ability", {})
    device = build_device_from_abilities(
        device_info=device_info, device_abilities=abilities
    )
    await device.async_handle_update()
    return device


_dynamic_types: dict[str, type] = {}


@lru_cache(maxsize=512)
def _lookup_cached_type(
    device_type: str, hardware_version: str, firmware_version: str
) -> Optional[type]:
    """Lookup."""
    lookup_string = _caclulate_device_type_name(
        device_type, hardware_version, firmware_version
    ).strip(":")
    return _dynamic_types.get(lookup_string)


def build_device_from_abilities(
    device_info: DeviceInfo, device_abilities: dict
) -> BaseDevice:
    """build_device_from_abilities."""
    cached_type = _lookup_cached_type(
        device_info.device_type,
        device_info.hdware_version,
        device_info.fmware_version,
    )

    if cached_type is None:
        device_type_name = _caclulate_device_type_name(
            device_info.device_type,
            device_info.hdware_version,
            device_info.fmware_version,
        )

        base_class = BaseDevice

        cached_type = _build_cached_type(
            type_string=device_type_name,
            device_abilities=device_abilities,
            base_class=base_class,
        )

        _dynamic_types[device_type_name] = cached_type

    component = cached_type(device=device_info)

    return component


def _caclulate_device_type_name(
    device_type: str, hardware_version: str, firmware_version: str
) -> str:
    """_caclulate_device_type_name."""
    return f"{device_type}:{hardware_version}:{firmware_version}"


def _build_cached_type(
    type_string: str, device_abilities: dict, base_class: type
) -> type:
    """_build_cached_type."""
    mixin_classes = set()

    for key, _value in device_abilities.items():
        clsx = None
        cls = _ABILITY_MATRIX.get(key)

        # Check if for this ability the device exposes the X version
        x_key = f"{key}X"
        x_version_ability = device_abilities.get(x_key)
        if x_version_ability is not None:
            clsx = _ABILITY_MATRIX.get(x_key)

        # Now, if we have both the clsx and the cls, prefer the clsx, otherwise go for the cls
        if clsx is not None:
            mixin_classes.add(clsx)
        elif cls is not None:
            mixin_classes.add(cls)

    classes_list = list(mixin_classes)
    classes_list.append(base_class)
    m = type(type_string, tuple(classes_list), {"_abilities_spec": device_abilities})
    return m
