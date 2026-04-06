"""Transport abstractions for the local provider."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Mapping, Optional

from ..core.exceptions import DreoDeviceNotFoundError, DreoProviderUnavailableError
from .config import LocalConfig
from .discovery import LocalDeviceDescriptor


def _device_key(device: LocalDeviceDescriptor) -> str:
    return device.serial_number or device.device_id or device.host


class LocalTransport(ABC):
    """Abstract transport for talking to local devices."""

    @abstractmethod
    def get_state(self, descriptor: LocalDeviceDescriptor, config: LocalConfig) -> Mapping[str, Any]:
        """Return a local state payload."""

    @abstractmethod
    def set_state(
        self,
        descriptor: LocalDeviceDescriptor,
        config: LocalConfig,
        payload: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        """Send a local command and return its response payload."""


class NullLocalTransport(LocalTransport):
    """Placeholder transport used until the real LAN protocol exists."""

    def get_state(self, descriptor: LocalDeviceDescriptor, config: LocalConfig) -> Mapping[str, Any]:
        del descriptor, config
        raise DreoProviderUnavailableError(
            "No LocalTransport implementation is configured. Inject a transport before calling state APIs."
        )

    def set_state(
        self,
        descriptor: LocalDeviceDescriptor,
        config: LocalConfig,
        payload: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        del descriptor, config, payload
        raise DreoProviderUnavailableError(
            "No LocalTransport implementation is configured. Inject a transport before calling control APIs."
        )


class InMemoryLocalTransport(LocalTransport):
    """Simple transport useful for tests and early local integration work."""

    def __init__(self, states: Optional[Dict[str, Dict[str, Any]]] = None) -> None:
        self._states = {key: dict(value) for key, value in (states or {}).items()}

    def get_state(self, descriptor: LocalDeviceDescriptor, config: LocalConfig) -> Mapping[str, Any]:
        del config
        key = _device_key(descriptor)
        if key not in self._states:
            raise DreoDeviceNotFoundError("No in-memory local state found for {key}".format(key=key))
        return dict(self._states[key])

    def set_state(
        self,
        descriptor: LocalDeviceDescriptor,
        config: LocalConfig,
        payload: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        del config
        key = _device_key(descriptor)
        current = dict(self._states.get(key, {}))
        current.update(dict(payload))
        self._states[key] = current
        return dict(current)
