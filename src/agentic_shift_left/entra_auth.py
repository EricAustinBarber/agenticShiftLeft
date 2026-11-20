"""Microsoft Entra JWT validation boundary for the production API host."""
from __future__ import annotations

import json
import time
from dataclasses import dataclass
from urllib.request import urlopen
from typing import Any

from .identity import IdentityContext


class AuthenticationError(PermissionError):
    pass


@dataclass
class EntraSettings:
    tenant_id: str
    audience: str
    required_issuer: str | None = None
    jwks_ttl_seconds: int = 3600

    @property
    def issuer(self) -> str:
        return self.required_issuer or f"https://login.microsoftonline.com/{self.tenant_id}/v2.0"

    @property
    def openid_config_url(self) -> str:
        return f"https://login.microsoftonline.com/{self.tenant_id}/v2.0/.well-known/openid-configuration"


class EntraTokenValidator:
    """Validate bearer tokens using Entra discovery and JWKS metadata.

    PyJWT with its crypto extra is intentionally optional until the production
    API host is installed. The prototype API does not call this class.
    """

    def __init__(self, settings: EntraSettings):
        self.settings = settings
        self._jwks: dict[str, Any] | None = None
        self._jwks_expires = 0.0

    def _load_jwks(self) -> dict[str, Any]:
        now = time.time()
        if self._jwks and now < self._jwks_expires:
            return self._jwks
        try:
            with urlopen(self.settings.openid_config_url, timeout=10) as response:
                config = json.loads(response.read().decode("utf-8"))
            with urlopen(config["jwks_uri"], timeout=10) as response:
                self._jwks = json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            raise AuthenticationError(f"Unable to load Entra signing keys: {exc}") from exc
        self._jwks_expires = now + self.settings.jwks_ttl_seconds
        return self._jwks

    def validate(self, authorization_header: str | None) -> IdentityContext:
        if not authorization_header or not authorization_header.lower().startswith("bearer "):
            raise AuthenticationError("Bearer token required")
        token = authorization_header.split(" ", 1)[1].strip()
        try:
            import jwt
            from jwt import PyJWKClient
            jwks_client = PyJWKClient(self._jwks_uri())
            signing_key = jwks_client.get_signing_key_from_jwt(token)
            claims = jwt.decode(token, signing_key.key, algorithms=["RS256"],
                                audience=self.settings.audience,
                                issuer=self.settings.issuer)
        except ImportError as exc:
            raise AuthenticationError("JWT validation requires the web optional dependencies") from exc
        except Exception as exc:
            raise AuthenticationError(f"Invalid Entra token: {exc}") from exc
        return IdentityContext(
            subject_id=claims.get("oid") or claims.get("sub", ""),
            tenant_id=claims.get("tid", ""),
            display_name=claims.get("name"),
            user_principal_name=claims.get("preferred_username"),
            roles=tuple(claims.get("roles", [])),
        )

    def _jwks_uri(self) -> str:
        # Cache discovery separately through the same metadata path.
        with urlopen(self.settings.openid_config_url, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))["jwks_uri"]
