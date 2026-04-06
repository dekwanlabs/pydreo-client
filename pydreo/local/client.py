"""Local-only facade."""

from __future__ import annotations

from typing import Optional

from ..client import DreoClient as UnifiedDreoClient
from ..core.strategy import ConnectionStrategy
from .config import LocalConfig
from .discovery import LocalDiscoveryBackend
from .protocol import LocalProtocolAdapter
from .provider import LocalProvider
from .transport import LocalTransport


class DreoLocalClient(UnifiedDreoClient):
    """Local-only client facade built on top of LocalProvider."""

    def __init__(
        self,
        config: Optional[LocalConfig] = None,
        *,
        discovery: Optional[LocalDiscoveryBackend] = None,
        transport: Optional[LocalTransport] = None,
        protocol: Optional[LocalProtocolAdapter] = None,
    ) -> None:
        self._local_provider = LocalProvider(
            config=config,
            discovery=discovery,
            transport=transport,
            protocol=protocol,
        )
        super().__init__(
            providers=[self._local_provider],
            strategy=ConnectionStrategy.LOCAL_ONLY,
        )
