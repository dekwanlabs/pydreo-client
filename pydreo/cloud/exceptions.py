"""Cloud exception compatibility re-exports."""

from ..core.exceptions import (
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

__all__ = [
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
]
