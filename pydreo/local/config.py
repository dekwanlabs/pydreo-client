"""Configuration objects for local providers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple


@dataclass(frozen=True)
class LocalHostConfig:
    """Static local device seed used before a discovery protocol exists."""

    host: str
    port: int = 0
    serial_number: Optional[str] = None
    device_id: Optional[str] = None
    name: Optional[str] = None
    model: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_host(cls, host: str) -> "LocalHostConfig":
        """Build a host config from a plain host string."""
        return cls(host=host)


@dataclass(frozen=True)
class LocalConfig:
    """Runtime settings for the local provider."""

    known_hosts: Tuple[LocalHostConfig, ...] = ()
    auto_discover: bool = True
    discovery_timeout: float = 2.0
    metadata: Dict[str, Any] = field(default_factory=dict)
