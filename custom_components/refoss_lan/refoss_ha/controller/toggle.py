"""ToggleXMix."""
import logging
import traceback

from ..enums import Namespace
from ..device import DeviceInfo
from .device import BaseDevice
from ..exceptions import DeviceTimeoutError

_LOGGER = logging.getLogger(__name__)


class ToggleXMix(BaseDevice):
    """A device."""

    def __init__(self, device: DeviceInfo):
        """Initialize."""
        self.device = device
        self.togglex_status = {}
        super().__init__(device)

    def is_on(self, channel=0) -> bool | None:
        """is_on(self, channel)."""
        return self.togglex_status.get(channel, None)

    async def async_handle_update(self):
        """Update device state,65535 get all channel."""
        payload = {"togglex": {"channel": 65535}}
        res = await self.async_execute_cmd(
            device_uuid=self.uuid,
            method="GET",
            namespace=Namespace.CONTROL_TOGGLEX,
            payload=payload,
        )

        if res is not None:
            data = res.get("payload", {})
            payload = data["togglex"]
            if payload is None:
                _LOGGER.debug(
                    f"{data} could not find 'togglex' attribute in push notification data"
                )

            elif isinstance(payload, list):
                for c in payload:
                    channel = c["channel"]
                    switch_state = c["onoff"] == 1
                    self.togglex_status[channel] = switch_state

            elif isinstance(payload, dict):
                channel = payload["channel"]
                switch_state = payload["onoff"] == 1
                self.togglex_status[channel] = switch_state
        await super().async_handle_update()

    async def async_turn_off(self, channel=0) -> None:
        """Turn off."""
        payload = {"togglex": {"onoff": 0, "channel": channel}}
        try:
            res = await self.async_execute_cmd(
                device_uuid=self.uuid,
                method="SET",
                namespace=Namespace.CONTROL_TOGGLEX,
                payload=payload,
            )
            if res is not None:
                self.togglex_status[channel] = False
        except DeviceTimeoutError:
            pass

    async def async_turn_on(self, channel=0) -> None:
        """Turn on."""
        payload = {"togglex": {"onoff": 1, "channel": channel}}
        try:
            res = await self.async_execute_cmd(
                device_uuid=self.uuid,
                method="SET",
                namespace=Namespace.CONTROL_TOGGLEX,
                payload=payload,
            )
            if res is not None:
                self.togglex_status[channel] = True
        except DeviceTimeoutError:
            pass

    async def async_toggle(self, channel=0) -> None:
        """Toggle."""
        if self.is_on(channel=channel):
            await self.async_turn_off(channel=channel)
        else:
            await self.async_turn_on(channel=channel)
