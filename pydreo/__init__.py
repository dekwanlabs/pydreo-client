"""Public package exports for pydreo."""

from .version import __version__
from .client import DreoClient
from .cloud.auth import CloudConfig
from .cloud.client import DreoCloudClient
from .core import (
    CommandResult,
    ConnectionStrategy,
    DeviceIdentity,
    DeviceInfo,
    DeviceState,
    DreoAccessDeniedException,
    DreoAuthenticationError,
    DreoBusinessError,
    DreoBusinessException,
    DreoConfigurationError,
    DreoConnectionError,
    DreoDeviceNotFoundError,
    DreoError,
    DreoException,
    DreoFlowControlException,
    DreoOperationError,
    DreoProviderUnavailableError,
    DreoRateLimitError,
    DreoUnsupportedFeatureError,
    ProviderKind,
)
from .local.client import DreoLocalClient
from .local.config import LocalConfig, LocalHostConfig

__all__ = [
    "CloudConfig",
    "CommandResult",
    "ConnectionStrategy",
    "DeviceIdentity",
    "DeviceInfo",
    "DeviceState",
    "DreoAccessDeniedException",
    "DreoAuthenticationError",
    "DreoBusinessError",
    "DreoBusinessException",
    "DreoClient",
    "DreoCloudClient",
    "DreoConfigurationError",
    "DreoConnectionError",
    "DreoDeviceNotFoundError",
    "DreoError",
    "DreoException",
    "DreoFlowControlException",
    "DreoLocalClient",
    "DreoOperationError",
    "DreoProviderUnavailableError",
    "DreoRateLimitError",
    "DreoUnsupportedFeatureError",
    "LocalConfig",
    "LocalHostConfig",
    "ProviderKind",
]
