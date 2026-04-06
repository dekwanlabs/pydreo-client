"""Tests for the local provider shell."""

from __future__ import annotations

import unittest

from pydreo.local.config import LocalConfig, LocalHostConfig
from pydreo.local.provider import LocalProvider
from pydreo.local.transport import InMemoryLocalTransport


class LocalProviderTests(unittest.TestCase):
    """Verify the built-in local shell is already usable for integration work."""

    def test_local_provider_uses_static_hosts_and_in_memory_transport(self) -> None:
        provider = LocalProvider(
            config=LocalConfig(
                known_hosts=(
                    LocalHostConfig(
                        host="192.168.1.20",
                        serial_number="LOCAL-001",
                        name="Desk Fan",
                    ),
                )
            ),
            transport=InMemoryLocalTransport({"LOCAL-001": {"power": "on", "speed": 2}}),
        )

        devices = provider.discover_devices()
        state = provider.get_device_state("LOCAL-001")
        result = provider.set_device_state("LOCAL-001", power="off")

        self.assertEqual(len(devices), 1)
        self.assertEqual(devices[0].identity.serial_number, "LOCAL-001")
        self.assertEqual(state.properties["power"], "on")
        self.assertEqual(result.raw["power"], "off")


if __name__ == "__main__":
    unittest.main()
