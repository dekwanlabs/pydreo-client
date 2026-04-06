"""Discovery backends for the local provider."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Tuple

from .config import LocalConfig, LocalHostConfig


@dataclass(frozen=True)
class LocalDeviceDescriptor:
    """A discovered local device."""

    host: str
    port: int = 0
    serial_number: Optional[str] = None
    device_id: Optional[str] = None
    name: Optional[str] = None
    model: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def aliases(self) -> Tuple[str, ...]:
        """Return alternate lookup keys."""
        aliases = [self.host]
        if self.serial_number:
            aliases.append(self.serial_number)
        if self.device_id:
            aliases.append(self.device_id)
        return tuple(dict.fromkeys(aliases))


class LocalDiscoveryBackend(ABC):
    """Abstract local discovery integration point."""

    @abstractmethod
    def discover(self, config: LocalConfig) -> List[LocalDeviceDescriptor]:
        """Return local device descriptors."""


class StaticLocalDiscovery(LocalDiscoveryBackend):
    """Discovery backend that returns statically configured local devices."""

    def __init__(self, descriptors: Optional[Iterable[LocalDeviceDescriptor]] = None) -> None:
        self._descriptors = list(descriptors or ())

    def discover(self, config: LocalConfig) -> List[LocalDeviceDescriptor]:
        configured = [self._from_host_config(host) for host in config.known_hosts]
        return configured + list(self._descriptors)

    @staticmethod
    def _from_host_config(host: LocalHostConfig) -> LocalDeviceDescriptor:
        return LocalDeviceDescriptor(
            host=host.host,
            port=host.port,
            serial_number=host.serial_number,
            device_id=host.device_id,
            name=host.name,
            model=host.model,
            metadata=dict(host.metadata),
        )
