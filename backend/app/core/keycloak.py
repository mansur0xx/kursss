import base64
import json
import time
from typing import Any

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User
from app.repositories.user_repository import UserRepository


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def _decode_jwt_unverified(token: str) -> tuple[dict[str, Any], dict[str, Any]] | None:
    parts = token.split(".")
    if len(parts) != 3:
        return None
    try:
        header = json.loads(_b64url_decode(parts[0]).decode("utf-8"))
        payload = json.loads(_b64url_decode(parts[1]).decode("utf-8"))
        if not isinstance(header, dict) or not isinstance(payload, dict):
            return None
        return header, payload
    except (ValueError, UnicodeDecodeError):
        return None


def _extract_role(payload: dict[str, Any]) -> str:
    realm_roles = payload.get("realm_access", {}).get("roles", [])
    if not isinstance(realm_roles, list):
        return "student"
    for priority_role in ("admin", "teacher", "student"):
        if priority_role in realm_roles:
            return priority_role
    return "student"


def _audience_matches(payload: dict[str, Any], expected_aud: str) -> bool:
    aud = payload.get("aud")
    if isinstance(aud, str):
        return aud == expected_aud
    if isinstance(aud, list):
        return expected_aud in aud
    return False


def verify_keycloak_token(token: str) -> dict[str, Any] | None:
    """
    Keycloak OIDC JWT токенін тексеру:
    - alg RS256 болса, Keycloak issuer, aud ('quizai-api') және exp мерзімін тексереді.
    - Егер Keycloak JWKS қолжетімді болса, кілт ID (kid) сәйкестігін тексереді.
    """
    decoded = _decode_jwt_unverified(token)
    if decoded is None:
        return None
    header, payload = decoded

    if header.get("alg") == "HS256":
        return None

    iss = payload.get("iss")
    if iss != settings.keycloak_issuer:
        return None

    if not _audience_matches(payload, settings.KEYCLOAK_AUDIENCE):
        return None

    exp = payload.get("exp")
    if not isinstance(exp, int) or exp < int(time.time()):
        return None

    kid = header.get("kid")
    if kid:
        try:
            with httpx.Client(timeout=3.0) as client:
                resp = client.get(settings.keycloak_jwks_url)
                resp.raise_for_status()
                keys = resp.json().get("keys", [])
                if not any(k.get("kid") == kid for k in keys):
                    return None
        except httpx.HTTPError:
            pass

    return payload


def sync_keycloak_user(db: Session, payload: dict[str, Any]) -> User | None:
    """
    Keycloak токеніндегі пайдаланушыны PostgreSQL users кестесімен синхрондау (JIT provisioning).
    """
    sub = payload.get("sub")
    if not isinstance(sub, str) or not sub:
        return None

    email = payload.get("email") or payload.get("preferred_username") or f"{sub}@quizai.local"
    full_name = (
        payload.get("name")
        or f"{payload.get('given_name', '')} {payload.get('family_name', '')}".strip()
        or email.split("@")[0]
    )
    role = _extract_role(payload)

    repo = UserRepository(db)
    user = repo.get_by_keycloak_id(sub)
    if user is None:
        user = repo.get_by_email(email)
        if user is not None:
            user.keycloak_id = sub
            user.role = role
            return repo.save(user)
        return repo.create(
            email=email,
            full_name=full_name[:120],
            role=role,
            keycloak_id=sub,
        )

    changed = False
    if user.role != role:
        user.role = role
        changed = True
    if user.email != email:
        user.email = email
        changed = True
    return repo.save(user) if changed else user
