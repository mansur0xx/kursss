from dataclasses import dataclass
from typing import Any, Protocol
from urllib.error import URLError

import jwt

APP_ROLES = ("admin", "teacher", "student")


class AuthUnavailableError(Exception):
    pass


@dataclass(frozen=True)
class Identity:
    keycloak_id: str
    email: str
    full_name: str
    role: str | None


class TokenVerifier(Protocol):
    def verify(self, token: str) -> dict[str, Any]: ...


class KeycloakVerifier:
    def __init__(self, issuer: str, jwks_url: str, audience: str) -> None:
        self.issuer = issuer
        self.audience = audience
        self._jwks = jwt.PyJWKClient(jwks_url, cache_keys=True)

    def verify(self, token: str) -> dict[str, Any]:
        try:
            key = self._jwks.get_signing_key_from_jwt(token)
        except (jwt.PyJWKClientConnectionError, URLError, OSError) as exc:
            raise AuthUnavailableError("Keycloak JWKS қолжетімсіз") from exc
        return jwt.decode(
            token,
            key.key,
            algorithms=["RS256"],
            issuer=self.issuer,
            audience=self.audience,
            options={"require": ["exp", "iat", "iss", "sub", "aud"]},
        )


def identity_from_claims(claims: dict[str, Any]) -> Identity:
    sub = str(claims["sub"])
    email = str(claims.get("email") or claims.get("preferred_username") or f"{sub}@quizai.local")
    full_name = str(
        claims.get("name")
        or f"{claims.get('given_name', '')} {claims.get('family_name', '')}".strip()
        or email.split("@")[0]
    )[:120]
    roles = set(claims.get("realm_access", {}).get("roles", []))
    role = next((r for r in APP_ROLES if r in roles), None)
    return Identity(
        keycloak_id=sub,
        email=email,
        full_name=full_name,
        role=role,
    )
