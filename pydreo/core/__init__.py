"""Core abstractions shared by all providers."""

from .exceptions import (
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
)
from .models import CommandResult, DeviceIdentity, DeviceInfo, DeviceState, ProviderKind
from .provider import BaseProvider
from .strategy import ConnectionStrategy

__all__ = [
    "BaseProvider",
    "CommandResult",
    "ConnectionStrategy",
    "DeviceIdentity",
    "DeviceInfo",
    "DeviceState",
    "DreoAccessDeniedException",
    "DreoAuthenticationError",
    "DreoBusinessError",
    "DreoBusinessException",
    "DreoConfigurationError",
    "DreoConnectionError",
    "DreoDeviceNotFoundError",
    "DreoError",
    "DreoException",
    "DreoFlowControlException",
    "DreoOperationError",
    "DreoProviderUnavailableError",
    "DreoRateLimitError",
    "DreoUnsupportedFeatureError",
    "ProviderKind",
]
