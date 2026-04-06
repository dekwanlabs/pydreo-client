"""Tests for the unified client facade and provider routing."""

from __future__ import annotations

import unittest

from pydreo import ConnectionStrategy, DreoClient
from pydreo.core.exceptions import DreoOperationError
from pydreo.core.models import CommandResult, DeviceIdentity, DeviceInfo, DeviceState, ProviderKind
from pydreo.core.provider import BaseProvider


class FakeProvider(BaseProvider):
    """Small fake provider used to test routing and merge behavior."""

    def __init__(
        self,
        kind: ProviderKind,
        *,
        devices=None,
        state=None,
        fail_reads: bool = False,
    ) -> None:
        self.kind = kind
        super().__init__(name="{kind}-fake".format(kind=kind.value))
        self._devices = list(devices or [])
        self._state = state
        self._fail_reads = fail_reads

    def discover_devices(self):
        return list(self._devices)

    def get_device_state(self, device):
        del device
        if self._fail_reads:
            raise DreoOperationError("{name} failed".format(name=self.name))
        return self._state

    def set_device_state(self, device, **changes):
        identity = DeviceIdentity(serial_number=str(device))
        return CommandResult(identity=identity, source=self.kind, changes=dict(changes))


class DreoClientTests(unittest.TestCase):
    """Behavioral tests for the unified provider facade."""

    def setUp(self) -> None:
        self.identity = DeviceIdentity(serial_number="SN-001")
        self.cloud_device = DeviceInfo(
            identity=self.identity,
            name="Bedroom Fan",
            sources=(ProviderKind.CLOUD.value,),
            metadata={"endpoint": "cloud"},
            provider_payloads={ProviderKind.CLOUD.value: {"deviceSn": "SN-001"}},
        )
        self.local_device = DeviceInfo(
            identity=self.identity,
            model="DR-HAF001",
            sources=(ProviderKind.LOCAL.value,),
            metadata={"host": "192.168.1.10"},
            provider_payloads={ProviderKind.LOCAL.value: {"host": "192.168.1.10"}},
        )

    def test_discovery_merges_same_device_from_multiple_providers(self) -> None:
        cloud = FakeProvider(ProviderKind.CLOUD, devices=[self.cloud_device])
        local = FakeProvider(ProviderKind.LOCAL, devices=[self.local_device])
        client = DreoClient(
            providers=[cloud, local],
            strategy=ConnectionStrategy.AUTO,
        )

        devices = client.discover_devices()

        self.assertEqual(len(devices), 1)
        merged = devices[0]
        self.assertEqual(merged.identity.serial_number, "SN-001")
        self.assertEqual(set(merged.sources), {"cloud", "local"})
        self.assertEqual(merged.name, "Bedroom Fan")
        self.assertEqual(merged.model, "DR-HAF001")

    def test_local_preferred_falls_back_to_cloud(self) -> None:
        local = FakeProvider(
            ProviderKind.LOCAL,
            state=DeviceState(identity=self.identity, properties={"power": "on"}, source=ProviderKind.LOCAL),
            fail_reads=True,
        )
        cloud = FakeProvider(
            ProviderKind.CLOUD,
            state=DeviceState(identity=self.identity, properties={"power": "off"}, source=ProviderKind.CLOUD),
        )
        client = DreoClient(
            providers=[local, cloud],
            strategy=ConnectionStrategy.LOCAL_PREFERRED,
        )

        state = client.get_device_state("SN-001")

        self.assertEqual(state.source, ProviderKind.CLOUD)
        self.assertEqual(state.properties["power"], "off")


if __name__ == "__main__":
    unittest.main()
