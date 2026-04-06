"""Cloud authentication helpers and configuration."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
import re
from typing import Optional

from .const import BASE_URL, EU_BASE_URL, REQUEST_TIMEOUT, USER_AGENT

_MD5_HEX_RE = re.compile(r"^[0-9a-f]{32}$", re.IGNORECASE)


@dataclass
class CloudConfig:
    """Cloud provider configuration."""

    username: Optional[str] = None
    password: Optional[str] = None
    access_token: Optional[str] = None
    endpoint: Optional[str] = None
    user_agent: str = USER_AGENT
    request_timeout: float = REQUEST_TIMEOUT

    def resolved_endpoint(self) -> Optional[str]:
        """Return the current endpoint, inferring it from the token when needed."""
        if self.endpoint:
            return self.endpoint
        if self.access_token:
            return resolve_cloud_endpoint(self.access_token)
        return None


def prepare_cloud_password(password: str) -> str:
    """Return the MD5 digest expected by the cloud login endpoint.

    Already-hashed MD5 digests are preserved to avoid double hashing while
    older callers are migrated to passing plaintext passwords.
    """

    if _MD5_HEX_RE.fullmatch(password):
        return password

    return hashlib.md5(password.encode("utf-8")).hexdigest()


def extract_token_region(access_token: Optional[str]) -> str:
    """Extract the region suffix from an access token."""
    if not access_token or ":" not in access_token:
        return "NA"
    raw_region = access_token.split(":", 1)[1].upper()
    if raw_region in ("EU", "NA"):
        return raw_region
    return "NA"


def strip_token_region(access_token: Optional[str]) -> Optional[str]:
    """Remove the region suffix from an access token."""
    if not access_token:
        return access_token
    return access_token.split(":", 1)[0]


def resolve_cloud_endpoint(access_token: Optional[str]) -> str:
    """Resolve the API endpoint from the access token region suffix."""
    if extract_token_region(access_token) == "EU":
        return EU_BASE_URL
    return BASE_URL
