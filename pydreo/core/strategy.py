"""Provider selection strategies."""

from __future__ import annotations

from enum import Enum
from typing import Iterable, Tuple

from .models import ProviderKind


class ConnectionStrategy(str, Enum):
    """How the facade should route requests across providers."""

    CLOUD_ONLY = "cloud_only"
    LOCAL_ONLY = "local_only"
    LOCAL_PREFERRED = "local_preferred"
    CLOUD_PREFERRED = "cloud_preferred"
    AUTO = "auto"

    @classmethod
    def coerce(cls, value: "ConnectionStrategy") -> "ConnectionStrategy":
        """Allow string or enum inputs."""
        if isinstance(value, cls):
            return value
        return cls(value)

    def provider_priority(self) -> Tuple[ProviderKind, ...]:
        """Return provider order for this strategy."""
        if self == self.CLOUD_ONLY:
            return (ProviderKind.CLOUD,)
        if self == self.LOCAL_ONLY:
            return (ProviderKind.LOCAL,)
        if self == self.CLOUD_PREFERRED:
            return (ProviderKind.CLOUD, ProviderKind.LOCAL)
        return (ProviderKind.LOCAL, ProviderKind.CLOUD)

    def as_list(self) -> Iterable[str]:
        """Human-friendly provider priority."""
        return tuple(kind.value for kind in self.provider_priority())
