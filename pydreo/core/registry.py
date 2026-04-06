"""Provider orchestration and device merge logic."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

from .exceptions import DreoConfigurationError, DreoOperationError
from .models import CommandResult, DeviceIdentity, DeviceInfo, DeviceReference, DeviceState, ProviderKind
from .provider import BaseProvider
from .strategy import ConnectionStrategy


def _normalize_lookup_key(value: str) -> str:
    return value.strip().lower()


class ProviderRegistry:
    """Coordinate multi-provider reads, writes, and device discovery."""

    def __init__(self, providers: Sequence[BaseProvider]) -> None:
        if not providers:
            raise DreoConfigurationError("At least one provider must be configured")

        self._providers: Dict[ProviderKind, BaseProvider] = {}
        for provider in providers:
            if provider.kind in self._providers:
                raise DreoConfigurationError(
                    "Duplicate provider configured for kind: {kind}".format(kind=provider.kind.value)
                )
            self._providers[provider.kind] = provider

        self._device_sources: Dict[str, List[ProviderKind]] = {}

    def authenticate_all(self) -> Dict[ProviderKind, Any]:
        """Authenticate every configured provider and return their results."""
        return {kind: provider.authenticate() for kind, provider in self._providers.items()}

    def discover_devices(self) -> List[DeviceInfo]:
        """Merge device discovery results across providers."""
        merged: Dict[str, DeviceInfo] = {}
        errors: List[str] = []
        self._device_sources = {}

        for kind, provider in self._providers.items():
            try:
                devices = provider.discover_devices()
            except Exception as err:  # pragma: no cover - preserved for diagnostics
                errors.append("{provider}: {error}".format(provider=provider.name, error=err))
                continue

            for device in devices:
                key = _normalize_lookup_key(device.identity.canonical_id())
                self._device_sources.setdefault(key, [])
                if kind not in self._device_sources[key]:
                    self._device_sources[key].append(kind)
                if key in merged:
                    merged[key] = merged[key].merged_with(device)
                else:
                    merged[key] = device

        if not merged and errors:
            raise DreoOperationError("No provider returned device data", errors)

        return list(merged.values())

    def get_device_state(
        self,
        device: DeviceReference,
        *,
        strategy: ConnectionStrategy,
    ) -> DeviceState:
        """Resolve the best provider and fetch a device state."""
        errors: List[str] = []
        for provider in self._ordered_providers(strategy, device=device):
            try:
                return provider.get_device_state(device)
            except Exception as err:
                errors.append("{provider}: {error}".format(provider=provider.name, error=err))
        raise DreoOperationError("All providers failed to fetch device state", errors)

    def set_device_state(
        self,
        device: DeviceReference,
        *,
        changes: Dict[str, Any],
        strategy: ConnectionStrategy,
    ) -> CommandResult:
        """Resolve the best provider and send a device command."""
        errors: List[str] = []
        for provider in self._ordered_providers(strategy, device=device):
            try:
                return provider.set_device_state(device, **changes)
            except Exception as err:
                errors.append("{provider}: {error}".format(provider=provider.name, error=err))
        raise DreoOperationError("All providers failed to update device state", errors)

    def _ordered_providers(
        self,
        strategy: ConnectionStrategy,
        *,
        device: Optional[DeviceReference] = None,
    ) -> List[BaseProvider]:
        requested = ConnectionStrategy.coerce(strategy).provider_priority()
        available = self._providers_for_device(device)
        ordered = [self._providers[kind] for kind in requested if kind in self._providers and kind in available]

        if strategy in (ConnectionStrategy.CLOUD_ONLY, ConnectionStrategy.LOCAL_ONLY) and not ordered:
            raise DreoConfigurationError(
                "Requested strategy {strategy} does not match any configured provider".format(
                    strategy=strategy.value
                )
            )

        for kind, provider in self._providers.items():
            if kind in available and provider not in ordered:
                ordered.append(provider)
        return ordered

    def _providers_for_device(self, device: Optional[DeviceReference]) -> List[ProviderKind]:
        if device is None:
            return list(self._providers.keys())

        key = self._lookup_key_for_device(device)
        known_sources = self._device_sources.get(key)
        if known_sources:
            return known_sources
        return list(self._providers.keys())

    @staticmethod
    def _lookup_key_for_device(device: DeviceReference) -> str:
        if isinstance(device, DeviceIdentity):
            return _normalize_lookup_key(device.canonical_id())
        return _normalize_lookup_key(device)
