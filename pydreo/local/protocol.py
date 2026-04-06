"""Protocol adapters for the local provider."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Optional

from ..core.models import (
    DeviceIdentity,
    DeviceInfo,
    DeviceState,
    ProviderKind,
    as_dict,
    maybe_online,
)
from .discovery import LocalDeviceDescriptor


class LocalProtocolAdapter(ABC):
    """Translate local transport payloads into normalized core models."""

    @abstractmethod
    def map_device_info(self, descriptor: LocalDeviceDescriptor) -> DeviceInfo:
        """Map a discovery descriptor to a normalized device."""

    @abstractmethod
    def map_device_state(self, descriptor: LocalDeviceDescriptor, payload: Mapping[str, Any]) -> DeviceState:
        """Map a state payload to a normalized device state."""

    @abstractmethod
    def build_command_payload(
        self,
        descriptor: LocalDeviceDescriptor,
        changes: Mapping[str, Any],
    ) -> Dict[str, Any]:
        """Build a provider-specific command payload."""


class PassthroughLocalProtocol(LocalProtocolAdapter):
    """Default adapter used until the real local protocol is implemented."""

    def map_device_info(self, descriptor: LocalDeviceDescriptor) -> DeviceInfo:
        identity = DeviceIdentity(
            serial_number=descriptor.serial_number,
            device_id=descriptor.device_id,
            ip_address=descriptor.host,
            display_name=descriptor.name,
            aliases=descriptor.aliases(),
        )
        return DeviceInfo(
            identity=identity,
            name=descriptor.name,
            model=descriptor.model,
            category="local",
            online=True,
            sources=(ProviderKind.LOCAL.value,),
            metadata={"host": descriptor.host, "port": descriptor.port, **descriptor.metadata},
            provider_payloads={
                ProviderKind.LOCAL.value: {
                    "host": descriptor.host,
                    "port": descriptor.port,
                    "serial_number": descriptor.serial_number,
                    "device_id": descriptor.device_id,
                    "name": descriptor.name,
                    "model": descriptor.model,
                    "metadata": dict(descriptor.metadata),
                }
            },
        )

    def map_device_state(self, descriptor: LocalDeviceDescriptor, payload: Mapping[str, Any]) -> DeviceState:
        identity = DeviceIdentity(
            serial_number=descriptor.serial_number,
            device_id=descriptor.device_id,
            ip_address=descriptor.host,
            display_name=descriptor.name,
            aliases=descriptor.aliases(),
        )
        properties = self._extract_properties(payload)
        online = self._extract_online(payload)
        return DeviceState(
            identity=identity,
            properties=properties,
            source=ProviderKind.LOCAL,
            online=online if online is not None else True,
            timestamp=datetime.now(timezone.utc),
            raw=dict(payload),
        )

    def build_command_payload(
        self,
        descriptor: LocalDeviceDescriptor,
        changes: Mapping[str, Any],
    ) -> Dict[str, Any]:
        del descriptor
        return dict(changes)

    @staticmethod
    def _extract_properties(payload: Mapping[str, Any]) -> Dict[str, Any]:
        for key in ("state", "status", "properties", "reported"):
            value = payload.get(key)
            if isinstance(value, Mapping):
                return dict(value)
        return as_dict(payload)

    @staticmethod
    def _extract_online(payload: Mapping[str, Any]) -> Optional[bool]:
        for key in ("online", "is_online", "available", "status"):
            if key in payload:
                online = maybe_online(payload.get(key))
                if online is not None:
                    return online
        return None
