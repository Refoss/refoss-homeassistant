"""Refoss exceptions."""
from __future__ import annotations


class RefossError(Exception):
    """Base class for aioRefoss errors."""


class InvalidMessage(RefossError):
    """Exception raised when an invalid message is received."""


class DeviceTimeoutError(RefossError):
    """Exception raised when http request timeout."""


class SocketError(RefossError):
    """Exception raised when socket send msg."""
