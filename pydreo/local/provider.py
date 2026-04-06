"""Local provider implementation and extension points."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..core.exceptions import DreoDeviceNotFoundError
from ..core.models import CommandResult, DeviceIdentity, DeviceReference, DeviceState, ProviderKind
from ..core.provider import BaseProvider
from .config import LocalConfig
from .discovery import LocalDeviceDescriptor, LocalDiscoveryBackend, StaticLocalDiscovery
from .protocol import LocalProtocolAdapter, PassthroughLocalProtocol
from .transport import LocalTransport, NullLocalTransport


class LocalProvider(BaseProvider):
    """Composable provider shell for future LAN protocol implementations."""

    kind = ProviderKind.LOCAL

    def __init__(
        self,
        config: Optional[LocalConfig] = None,
        *,
        discovery: Optional[LocalDiscoveryBackend] = None,
        transport: Optional[LocalTransport] = None,
        protocol: Optional[LocalProtocolAdapter] = None,
        name: Optional[str] = None,
    ) -> None:
        super().__init__(name=name)
        self.config = config or LocalConfig()
        self.discovery = discovery or StaticLocalDiscovery()
        self.transport = transport or NullLocalTransport()
        self.protocol = protocol or PassthroughLocalProtocol()
        self._known_devices: Dict[str, LocalDeviceDescriptor] = {}

    @property
    def is_authenticated(self) -> bool:
        return True

    def authenticate(self) -> Dict[str, str]:
        """Local providers are ready immediately unless a custom transport says otherwise."""
        return {"status": "ready", "mode": "local"}

    def discover_devices(self) -> List:
        descriptors = self.discovery.discover(self.config)
        self._index_devices(descriptors)
        return [self.protocol.map_device_info(descriptor) for descriptor in descriptors]

    def get_device_state(self, device: DeviceReference) -> DeviceState:
        descriptor = self._resolve_descriptor(device)
        payload = self.transport.get_state(descriptor, self.config)
        return self.protocol.map_device_state(descriptor, payload)

    def set_device_state(self, device: DeviceReference, **changes: Any) -> CommandResult:
        descriptor = self._resolve_descriptor(device)
        payload = self.protocol.build_command_payload(descriptor, changes)
        response = self.transport.set_state(descriptor, self.config, payload)
        identity = DeviceIdentity(
            serial_number=descriptor.serial_number,
            device_id=descriptor.device_id,
            ip_address=descriptor.host,
            display_name=descriptor.name,
            aliases=descriptor.aliases(),
        )
        return CommandResult(
            identity=identity,
            source=self.kind,
            accepted=True,
            changes=dict(changes),
            raw=dict(response),
        )

    def _resolve_descriptor(self, device: DeviceReference) -> LocalDeviceDescriptor:
        if not self._known_devices:
            self.discover_devices()

        if isinstance(device, DeviceIdentity):
            candidates = [
                device.serial_number,
                device.device_id,
                device.ip_address,
                device.display_name,
            ]
        else:
            candidates = [device]

        for candidate in candidates:
            if candidate and candidate in self._known_devices:
                return self._known_devices[candidate]

        raise DreoDeviceNotFoundError(
            "Local provider could not resolve device: {device}".format(device=device)
        )

    def _index_devices(self, descriptors: List[LocalDeviceDescriptor]) -> None:
        index: Dict[str, LocalDeviceDescriptor] = {}
        for descriptor in descriptors:
            for alias in descriptor.aliases():
                index[alias] = descriptor
        self._known_devices = index
