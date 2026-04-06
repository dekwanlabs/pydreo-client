"""Unified Dreo client facade."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Sequence

from .cloud.auth import CloudConfig
from .cloud.provider import CloudProvider
from .core.exceptions import DreoConfigurationError
from .core.models import CommandResult, DeviceInfo, DeviceReference, DeviceState
from .core.provider import BaseProvider
from .core.registry import ProviderRegistry
from .core.strategy import ConnectionStrategy
from .local.config import LocalConfig
from .local.provider import LocalProvider


class DreoClient:
    """High-level client capable of orchestrating multiple providers."""

    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        *,
        cloud_config: Optional[CloudConfig] = None,
        local_config: Optional[LocalConfig] = None,
        providers: Optional[Sequence[BaseProvider]] = None,
        strategy: ConnectionStrategy = ConnectionStrategy.AUTO,
    ) -> None:
        self.strategy = ConnectionStrategy.coerce(strategy)
        self._providers = tuple(providers or self._build_default_providers(username, password, cloud_config, local_config))
        if not self._providers:
            raise DreoConfigurationError(
                "At least one provider or provider configuration must be supplied"
            )
        self._registry = ProviderRegistry(self._providers)

    @staticmethod
    def _build_default_providers(
        username: Optional[str],
        password: Optional[str],
        cloud_config: Optional[CloudConfig],
        local_config: Optional[LocalConfig],
    ) -> Iterable[BaseProvider]:
        providers: List[BaseProvider] = []

        if cloud_config is None and (username or password):
            cloud_config = CloudConfig(username=username, password=password)
        if cloud_config is not None:
            providers.append(CloudProvider(cloud_config))

        if local_config is not None:
            providers.append(LocalProvider(local_config))

        return providers

    @property
    def providers(self) -> Sequence[BaseProvider]:
        """Return configured providers."""
        return self._providers

    @property
    def is_authenticated(self) -> bool:
        """Return True when every provider has completed its setup/auth step."""
        return all(provider.is_authenticated for provider in self._providers)

    def authenticate(self) -> Dict[str, Any]:
        """Authenticate or prepare all configured providers."""
        results = self._registry.authenticate_all()
        serializable_results = {kind.value: value for kind, value in results.items()}
        if tuple(serializable_results.keys()) == ("cloud",):
            return serializable_results["cloud"]
        return serializable_results

    def login(self) -> Dict[str, Any]:
        """Compatibility alias for authenticate()."""
        return self.authenticate()

    def discover_devices(self) -> List[DeviceInfo]:
        """Discover devices across all configured providers."""
        return self._registry.discover_devices()

    def get_device_state(
        self,
        device: DeviceReference,
        *,
        strategy: Optional[ConnectionStrategy] = None,
    ) -> DeviceState:
        """Get a normalized device state."""
        return self._registry.get_device_state(device, strategy=strategy or self.strategy)

    def set_device_state(
        self,
        device: DeviceReference,
        *,
        strategy: Optional[ConnectionStrategy] = None,
        **changes: Any
    ) -> CommandResult:
        """Send device changes using the configured provider strategy."""
        return self._registry.set_device_state(
            device,
            changes=changes,
            strategy=strategy or self.strategy,
        )

    def get_devices(self) -> List[Dict[str, Any]]:
        """Compatibility helper returning normalized device dictionaries."""
        return [device.to_dict() for device in self.discover_devices()]

    def get_status(self, devicesn: str) -> Dict[str, Any]:
        """Compatibility helper returning a normalized device state dictionary."""
        return self.get_device_state(devicesn).to_dict()

    def update_status(self, devicesn: str, **kwargs: Any) -> Dict[str, Any]:
        """Compatibility helper returning a normalized command result dictionary."""
        return self.set_device_state(devicesn, **kwargs).to_dict()
