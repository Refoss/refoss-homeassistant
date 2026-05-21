"""socket_server."""

import asyncio
import json
import logging
import socket

from .exceptions import SocketError

_LOGGER = logging.getLogger(__name__)


def socket_init(port: int) -> socket.socket:
    """Create and bind a UDP socket for device discovery."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # SO_REUSEPORT allows multiple processes to bind the same port
    # and all receive datagrams (available on Linux/macOS, not Windows).
    if hasattr(socket, "SO_REUSEPORT"):
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except OSError:
            pass
    sock.bind(("", port))
    return sock


class Discovery(asyncio.DatagramProtocol):
    """Socket server."""

    def __init__(self, port: int = 9989) -> None:
        self.device_info: dict | None = None
        self.sock: socket.socket | None = None
        self.transport: asyncio.transports.DatagramTransport | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._port = port
        self._response_event = asyncio.Event()

    def connection_made(self, transport: asyncio.transports.DatagramTransport) -> None:
        """Handle connection made."""
        self.transport = transport

    async def initialize(self) -> None:
        """Initialize socket server."""
        try:
            self.sock = socket_init(self._port)
        except OSError as err:
            raise SocketError(err) from err
        self._loop = asyncio.get_running_loop()
        await self._loop.create_datagram_endpoint(lambda: self, sock=self.sock)

    async def broadcast_msg(self, ip: str = "", wait_for: int = 0) -> dict | None:
        """Broadcast and wait for device response."""
        address = (ip, 9988)
        msg = json.dumps(
            {"id": "48cbd88f969eb3c486085cfe7b5eb1e4", "devName": "*"}
        ).encode("utf-8")
        try:
            self.transport.sendto(msg, address)
            if wait_for:
                try:
                    await asyncio.wait_for(
                        self._response_event.wait(), timeout=wait_for
                    )
                except asyncio.TimeoutError:
                    pass
        except Exception as err:
            raise SocketError(err) from err
        return self.device_info

    def datagram_received(self, data: bytes, addr: tuple[str, int]) -> None:
        """Handle incoming datagram messages."""
        try:
            json_str = data.decode("utf-8")
            data_dict = json.loads(json_str)
        except (UnicodeDecodeError, json.JSONDecodeError):
            _LOGGER.debug("Received invalid datagram from %s", addr)
            return
        _LOGGER.debug("Discovered device %s", data_dict)
        if "channels" in data_dict and "uuid" in data_dict:
            _LOGGER.info("Discovered device %s", data_dict.get("devName"))
            uuid = data_dict["uuid"]
            if self.device_info and self.device_info.get("uuid") == uuid:
                return
            self.device_info = data_dict
            self._response_event.set()

    def close_discovery(self) -> None:
        """Close discovery resources."""
        # transport 接管了 socket 生命周期，优先通过 transport 关闭
        if self.transport is not None:
            self.transport.close()
            self.transport = None
            self.sock = None
        elif self.sock is not None:
            self.sock.close()
            self.sock = None
        self.device_info = None
