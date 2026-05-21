"""http_device."""

from __future__ import annotations

import asyncio
from hashlib import md5
import json
import logging
import random
import string
import time

LOGGER = logging.getLogger(__name__)
from typing import Union

from aiohttp import ClientSession, ClientTimeout

from .enums import Namespace
from .util import BaseDictPayload, _underscore_to_camel
from .exceptions import DeviceTimeoutError, RefossError


class DeviceInfo(BaseDictPayload):
    """Base class."""

    # Maps internal attribute names to the original JSON keys.
    # This ensures to_dict() produces output that from_dict() can consume.
    _JSON_KEY_MAP: dict[str, str] = {
        "fmware_version": "devSoftWare",
        "hdware_version": "devHardWare",
        "inner_ip": "ip",
    }

    def __init__(
        self,
        uuid: str,
        dev_name: str,
        device_type: str,
        dev_soft_ware: str,
        dev_hard_ware: str,
        ip: str,
        port: str,
        mac: str,
        sub_type: str,
        channels: str | list[int],
        *args,
        **kwargs,
    ) -> None:
        """Create a HttpDeviceInfo."""
        super().__init__(*args, **kwargs)

        self.uuid = uuid
        self.dev_name = dev_name
        self.device_type = device_type
        self.fmware_version = dev_soft_ware
        self.hdware_version = dev_hard_ware
        self.inner_ip = ip
        self.port = port
        self.mac = mac
        self.sub_type = sub_type
        self.channels = channels
        self._session: ClientSession | None = None

    def set_session(self, session: ClientSession) -> None:
        """Set the aiohttp session."""
        self._session = session

    def to_dict(self) -> dict:
        """Convert to dict with correct JSON key names."""
        res = {}
        for k, v in vars(self).items():
            if k.startswith("_"):
                continue
            if k in self._JSON_KEY_MAP:
                new_key = self._JSON_KEY_MAP[k]
            else:
                new_key = _underscore_to_camel(k)
            res[new_key] = v
        return res

    def __str__(self) -> str:
        """Returns a string."""
        basic_info = f"{self.dev_name} ({self.device_type}, HW {self.hdware_version}, FW {self.fmware_version}, Uuid {self.uuid},channels {self.channels} )"
        return basic_info

    async def async_execute_cmd(
        self,
        device_uuid: str,
        method: str,
        namespace: Union[Namespace, str],
        payload: dict,
        timeout: int = 20,
    ):
        """async_execute_cmd."""
        message_dict, message_id = self._build_mqtt_message(
            method, namespace, payload, device_uuid
        )

        if self.device_type == "r10":
            path = f"http://{self.inner_ip}/config"
        else:
            path = f"http://{self.inner_ip}/public"

        try:
            session = self._session or ClientSession()
            owns_session = self._session is None
            try:
                async with session.post(
                    path,
                    json=message_dict,
                    timeout=ClientTimeout(total=timeout),
                ) as response:
                    data = await response.json()
                    if data is not None:
                        header = data.get("header", {})
                        messageId = header.get("messageId")
                        ack_method = header.get("method")
                        if messageId == message_id and ack_method == method + "ACK":
                            return data
                    return None
            finally:
                if owns_session:
                    await session.close()
        except asyncio.TimeoutError:
            namespace_val = (
                namespace.value if isinstance(namespace, Namespace) else namespace
            )
            LOGGER.debug(
                "Http timeout, ip: %s, device_type: %s, namespace: %s",
                self.inner_ip,
                self.device_type,
                namespace_val,
            )
            raise DeviceTimeoutError
        except Exception as e:
            namespace_val = (
                namespace.value if isinstance(namespace, Namespace) else namespace
            )
            LOGGER.debug(
                "Http fail: %s, ip: %s, device_type: %s, namespace: %s",
                e,
                self.inner_ip,
                self.device_type,
                namespace_val,
            )
            raise RefossError("Device connection failed") from e

    def _build_mqtt_message(
        self,
        method: str,
        namespace: Union[Namespace, str],
        payload: dict,
        destination_device_uuid: str,
    ) -> tuple[dict, str]:
        """Build message dict and return (data_dict, message_id)."""
        # Generate a random 16 byte string
        randomstring = "".join(
            random.SystemRandom().choice(string.ascii_uppercase + string.digits)
            for _ in range(16)
        )

        userkey = ""

        # Hash it as md5
        md5_hash = md5()
        md5_hash.update(randomstring.encode("utf8"))
        messageId = md5_hash.hexdigest().lower()
        timestamp = int(round(time.time()))

        # Hash the messageId, the key and the timestamp
        md5_hash = md5()
        strtohash = f"{messageId}{userkey}{timestamp}"
        md5_hash.update(strtohash.encode("utf8"))
        signature = md5_hash.hexdigest().lower()

        namespace_val = (
            namespace.value if isinstance(namespace, Namespace) else namespace
        )

        data = {
            "header": {
                "from": f"/app/{randomstring}/subscribe",
                "messageId": messageId,
                "method": method,
                "namespace": namespace_val,
                "payloadVersion": 1,
                "sign": signature,
                "timestamp": timestamp,
                "triggerSrc": "HA",
                "uuid": destination_device_uuid,
            },
            "payload": payload,
        }

        return data, messageId
