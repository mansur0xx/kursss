import logging
from functools import lru_cache

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import (
    AuthUnavailableError,
    KeycloakVerifier,
    TokenVerifier,
    identity_from_claims,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository

logger = logging.getLogger("quizai.auth")

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=settings.keycloak_auth_url,
    tokenUrl=settings.keycloak_token_url,
    scopes={"openid": "OpenID Connect"},
)


@lru_cache(maxsize=1)
def get_token_verifier() -> TokenVerifier:
    return KeycloakVerifier(
        issuer=settings.keycloak_issuer,
        jwks_url=settings.jwks_url,
        audience=settings.keycloak_audience,
    )


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
    verifier: TokenVerifier = Depends(get_token_verifier),
) -> User:
    try:
        claims = verifier.verify(token)
        identity = identity_from_claims(claims)
    except AuthUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Keycloak қолжетімсіз",
        ) from exc
    except (jwt.PyJWTError, KeyError, ValueError) as exc:
        logger.warning("Токен қабылданбады: %s: %s", type(exc).__name__, exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен жоқ, қате немесе мерзімі өткен",
        ) from exc

    if identity.role is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Keycloak-та қосымша рөлі берілмеген",
        )
    return UserRepository(db).sync(identity, identity.role)


def require_role(*roles: str):
    def checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Бұл әрекетке рұқсат жоқ",
            )
        return user

    return checker
