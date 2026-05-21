"""ElectricityXMix."""

import logging

from ..enums import Namespace
from ..device import DeviceInfo
from .device import BaseDevice

_LOGGER = logging.getLogger(__name__)


class ElectricityXMix(BaseDevice):
    """A device."""

    def __init__(self, device: DeviceInfo):
        """Initialize."""
        self.device = device
        self.electricity_status = {}
        super().__init__(device)

    def get_value(self, channel: int, subkey: str):
        """
        Returns the value for the given channel and subkey, or None if not found.
        """
        channel_status = self.electricity_status.get(channel, None)
        if channel_status is not None and subkey in channel_status:
            return channel_status.get(subkey, None)
        return None

    async def async_handle_update(self):
        """Update device state,65535 get all channel."""

        payload = {"electricity": {"channel": 65535}}
        res = await self.async_execute_cmd(
            device_uuid=self.uuid,
            method="GET",
            namespace=Namespace.CONTROL_ELECTRICITYX,
            payload=payload,
        )
        if res is not None:
            data = res.get("payload", {})
            payload = data.get("electricity")
            if payload is None:
                _LOGGER.debug(
                    "Could not find 'electricity' attribute in response: %s", data
                )

            elif isinstance(payload, list):
                for state in payload:
                    channel = state.get("channel", 0)
                    self.electricity_status[channel] = state
            else:
                _LOGGER.debug(
                    "ElectricityXMix unexpected payload type for %s: %s",
                    self.dev_name, type(payload).__name__,
                )
        else:
            _LOGGER.debug("ElectricityXMix update got None response for %s", self.dev_name)
        await super().async_handle_update()
