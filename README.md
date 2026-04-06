pydreo-client
=============

`pydreo-client` is now a provider-based Dreo SDK. The package still supports the original cloud-only usage, but the internal architecture has been rebuilt so we can add a real `local` module without duplicating client, device, and routing logic.

## What Changed in v2

- Added a formal `pydreo/` package with clear `core`, `cloud`, and `local` boundaries.
- Introduced a unified `DreoClient` facade that can orchestrate multiple providers.
- Migrated cloud access into a `CloudProvider` with separate auth and HTTP transport layers.
- Added a usable `LocalProvider` shell with config, discovery, protocol, and transport extension points.
- Preserved the cloud compatibility import path: `from pydreo.cloud.client import DreoClient`.

## Package Layout

```text
pydreo/
  client.py            # Unified facade
  core/                # Shared models, strategy, registry, exceptions
  cloud/               # Cloud provider implementation
  local/               # Local provider shell and extension points
```

## Installation

```sh
pip install pydreo-client
```

## Usage

### Cloud Only, Backward Compatible

```python
from pydreo.cloud.client import DreoClient

client = DreoClient("USERNAME", "PASSWORD")
client.login()

devices = client.get_devices()
status = client.get_status("DEVICE_SN")
client.update_status("DEVICE_SN", power="on")
```

### Unified Facade with Future Local Support

```python
from pydreo import CloudConfig, ConnectionStrategy, DreoClient, LocalConfig

client = DreoClient(
    cloud_config=CloudConfig(username="USERNAME", password="PASSWORD"),
    local_config=LocalConfig(),
    strategy=ConnectionStrategy.LOCAL_PREFERRED,
)

devices = client.discover_devices()
state = client.get_device_state("DEVICE_SN")
result = client.set_device_state("DEVICE_SN", power="on")
```

### Injecting a Local Transport During Development

```python
from pydreo import DreoLocalClient, LocalConfig, LocalHostConfig
from pydreo.local.transport import InMemoryLocalTransport

client = DreoLocalClient(
    config=LocalConfig(
        known_hosts=(
            LocalHostConfig(host="192.168.1.20", serial_number="LOCAL-001", name="Desk Fan"),
        ),
    ),
    transport=InMemoryLocalTransport({"LOCAL-001": {"power": "on", "speed": 2}}),
)

devices = client.discover_devices()
state = client.get_device_state("LOCAL-001")
```

## Extending the Local Module

The new local stack is deliberately composable:

- `LocalDiscoveryBackend` is where LAN discovery or manual device seeding should live.
- `LocalTransport` is where socket or protocol I/O should live.
- `LocalProtocolAdapter` is where payload translation should live.
- `LocalProvider` wires those pieces together and exposes the same contract as cloud.

That means the next local implementation can focus on protocol specifics without changing the public client surface again.

## Development

Run the built-in unit tests with:

```sh
python3 -m unittest discover -s tests -v
```

## License

Distributed under the MIT License. See `LICENSE` for more information.
