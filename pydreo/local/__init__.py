"""Local provider exports."""

from .config import LocalConfig, LocalHostConfig
from .provider import LocalProvider

__all__ = ["DreoLocalClient", "LocalConfig", "LocalHostConfig", "LocalProvider"]


def __getattr__(name):
    if name == "DreoLocalClient":
        from .client import DreoLocalClient

        return DreoLocalClient
    raise AttributeError(name)
