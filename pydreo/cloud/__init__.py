"""Cloud provider exports."""

from .auth import CloudConfig
from .provider import CloudProvider

__all__ = ["CloudConfig", "CloudProvider", "DreoClient", "DreoCloudClient"]


def __getattr__(name):
    if name in ("DreoClient", "DreoCloudClient"):
        from .client import DreoClient, DreoCloudClient

        exports = {
            "DreoClient": DreoClient,
            "DreoCloudClient": DreoCloudClient,
        }
        return exports[name]
    raise AttributeError(name)
