"""Provider-agnostic device models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Mapping, Optional, Tuple, Union

from .exceptions import DreoConfigurationError


class ProviderKind(str, Enum):
    """Built-in provider types."""

    CLOUD = "cloud"
    LOCAL = "local"


def _copy_mapping(value: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    return dict(value or {})


@dataclass(frozen=True)
class DeviceIdentity:
    """Stable identifiers used to correlate a device across providers."""

    serial_number: Optional[str] = None
    device_id: Optional[str] = None
    product_id: Optional[str] = None
    mac_address: Optional[str] = None
    ip_address: Optional[str] = None
    display_name: Optional[str] = None
    aliases: Tuple[str, ...] = ()

    def canonical_id(self) -> str:
        """Return the best available stable identifier for this device."""
        candidates = (
            self.serial_number,
            self.device_id,
            self.mac_address,
            self.ip_address,
            self.display_name,
        ) + self.aliases
        for candidate in candidates:
            if candidate:
                return candidate
        raise DreoConfigurationError("Device identity is missing a stable identifier")

    def merged_with(self, other: "DeviceIdentity") -> "DeviceIdentity":
        """Merge two partial identities into a single identity."""
        return DeviceIdentity(
            serial_number=self.serial_number or other.serial_number,
            device_id=self.device_id or other.device_id,
            product_id=self.product_id or other.product_id,
            mac_address=self.mac_address or other.mac_address,
            ip_address=self.ip_address or other.ip_address,
            display_name=self.display_name or other.display_name,
            aliases=tuple(dict.fromkeys(self.aliases + other.aliases)),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-friendly representation."""
        return {
            "serial_number": self.serial_number,
            "device_id": self.device_id,
            "product_id": self.product_id,
            "mac_address": self.mac_address,
            "ip_address": self.ip_address,
            "display_name": self.display_name,
            "aliases": list(self.aliases),
            "canonical_id": self.canonical_id(),
        }


@dataclass(frozen=True)
class DeviceInfo:
    """Normalized device discovery data."""

    identity: DeviceIdentity
    name: Optional[str] = None
    model: Optional[str] = None
    category: Optional[str] = None
    online: Optional[bool] = None
    sources: Tuple[str, ...] = ()
    metadata: Dict[str, Any] = field(default_factory=dict)
    provider_payloads: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def merged_with(self, other: "DeviceInfo") -> "DeviceInfo":
        """Merge discovery results from two providers."""
        return DeviceInfo(
            identity=self.identity.merged_with(other.identity),
            name=self.name or other.name,
            model=self.model or other.model,
            category=self.category or other.category,
            online=self.online if self.online is not None else other.online,
            sources=tuple(sorted(set(self.sources + other.sources))),
            metadata={**other.metadata, **self.metadata},
            provider_payloads={**other.provider_payloads, **self.provider_payloads},
        )

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-friendly representation."""
        return {
            "identity": self.identity.to_dict(),
            "name": self.name,
            "model": self.model,
            "category": self.category,
            "online": self.online,
            "sources": list(self.sources),
            "metadata": dict(self.metadata),
            "provider_payloads": {key: dict(value) for key, value in self.provider_payloads.items()},
        }


@dataclass(frozen=True)
class DeviceState:
    """Normalized device state."""

    identity: DeviceIdentity
    properties: Dict[str, Any] = field(default_factory=dict)
    source: ProviderKind = ProviderKind.CLOUD
    online: Optional[bool] = None
    timestamp: Optional[datetime] = None
    raw: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-friendly representation."""
        return {
            "identity": self.identity.to_dict(),
            "properties": dict(self.properties),
            "source": self.source.value,
            "online": self.online,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "raw": dict(self.raw),
        }


@dataclass(frozen=True)
class CommandResult:
    """Normalized command result."""

    identity: DeviceIdentity
    source: ProviderKind
    accepted: bool = True
    changes: Dict[str, Any] = field(default_factory=dict)
    raw: Dict[str, Any] = field(default_factory=dict)
    message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-friendly representation."""
        return {
            "identity": self.identity.to_dict(),
            "source": self.source.value,
            "accepted": self.accepted,
            "changes": dict(self.changes),
            "raw": dict(self.raw),
            "message": self.message,
        }


DeviceReference = Union[str, DeviceIdentity]


def as_dict(value: Any) -> Dict[str, Any]:
    """Convert arbitrary provider payloads into dictionaries."""
    if isinstance(value, Mapping):
        return dict(value)
    return {"value": value}


def maybe_online(value: Any) -> Optional[bool]:
    """Normalize common online flags."""
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return bool(value)
    if isinstance(value, str):
        lowered = value.lower()
        if lowered in ("online", "connected", "available", "true", "1"):
            return True
        if lowered in ("offline", "disconnected", "unavailable", "false", "0"):
            return False
    return None


def mapping_copy(value: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    """Public helper used by providers when copying response payloads."""
    return _copy_mapping(value)
