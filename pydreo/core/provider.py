"""Provider base classes."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, List, Optional

from .models import CommandResult, DeviceInfo, DeviceReference, DeviceState, ProviderKind


class BaseProvider(ABC):
    """Abstract provider contract."""

    kind: ProviderKind

    def __init__(self, *, name: Optional[str] = None) -> None:
        self.name = name or self.kind.value

    @property
    def is_authenticated(self) -> bool:
        """Return True if the provider is ready to handle requests."""
        return True

    def authenticate(self) -> Any:
        """Authenticate or prepare the provider."""
        return None

    @abstractmethod
    def discover_devices(self) -> List[DeviceInfo]:
        """Discover or enumerate devices available to this provider."""

    @abstractmethod
    def get_device_state(self, device: DeviceReference) -> DeviceState:
        """Fetch the current state of a device."""

    @abstractmethod
    def set_device_state(self, device: DeviceReference, **changes: Any) -> CommandResult:
        """Apply changes to a device."""
