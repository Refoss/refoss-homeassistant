"""socket_server."""
import asyncio
import json
import logging
import socket
from .exceptions import SocketError


_LOGGER = logging.getLogger(__name__)


def socket_init() -> socket.socket:
    """socket_init."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind(("", 9989))
    return sock


class Discovery(asyncio.DatagramProtocol):
    """Socket server."""

    def __init__(self) -> None:
        self.device_info = None
        self._loop = asyncio.get_event_loop()

    def connection_made(self, transport: asyncio.transports.DatagramTransport) -> None:
        """Handle connection made."""
        self.transport = transport

    async def initialize(self) -> None:
        """Initialize socket server."""
        self.sock = socket_init()
        await self._loop.create_datagram_endpoint(lambda: self, sock=self.sock)

    async def broadcast_msg(self, ip=str, wait_for: int = 0) -> dict:
        """Broadcast."""
        address = (ip, 9988)
        msg = json.dumps(
            {"id": "48cbd88f969eb3c486085cfe7b5eb1e4", "devName": "*"}
        ).encode("utf-8")
        try:
            self.transport.sendto(msg, address)
            if wait_for:
                await asyncio.sleep(wait_for)
        except Exception as err:
            raise SocketError(err) from err
        return self.device_info

    def datagram_received(self, data: bytes, addr: tuple[str, int]) -> None:
        """Handle incoming datagram messages."""
        json_str = format(data.decode("utf-8"))
        data_dict = json.loads(json_str)
        _LOGGER.debug(f"Discovered device {data_dict}")
        if "channels" in data_dict and "uuid" in data_dict:
            uuid = data_dict["uuid"]
            if self.device_info and (uuid in self.device_info):
                return
            self.device_info = data_dict

    def closeDiscovery(self):
        """Close."""
        if self.sock:
            self.sock.close()
        if self.transport:
            self.transport.close()
        self.device_info = None
