"""Core exception types used by the provider architecture."""

from __future__ import annotations

from typing import Iterable, Optional


class DreoError(Exception):
    """Base exception for all pydreo errors."""


class DreoConfigurationError(DreoError):
    """Raised when the client or provider is misconfigured."""


class DreoAuthenticationError(DreoError):
    """Raised when authentication fails or credentials are missing."""


class DreoConnectionError(DreoError):
    """Raised when a provider cannot reach the target service."""


class DreoBusinessError(DreoError):
    """Raised when the upstream API rejects the requested operation."""


class DreoRateLimitError(DreoError):
    """Raised when a provider rejects requests because of rate limiting."""


class DreoDeviceNotFoundError(DreoError):
    """Raised when the requested device cannot be resolved."""


class DreoProviderUnavailableError(DreoError):
    """Raised when a configured provider cannot service a request."""


class DreoUnsupportedFeatureError(DreoError):
    """Raised when a provider does not support a requested capability."""


class DreoOperationError(DreoError):
    """Raised when every candidate provider failed to complete an operation."""

    def __init__(self, message: str, errors: Optional[Iterable[str]] = None) -> None:
        self.errors = tuple(errors or ())
        suffix = ""
        if self.errors:
            suffix = " | details: " + "; ".join(self.errors)
        super().__init__(message + suffix)


# Compatibility aliases kept for cloud users of the old package.
DreoException = DreoError
DreoBusinessException = DreoBusinessError
DreoFlowControlException = DreoRateLimitError
DreoAccessDeniedException = DreoAuthenticationError
