from typing import NoReturn

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2AuthorizationCodeBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.keycloak import extract_role, verify_keycloak_token
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.exceptions import (
    AppError,
    BadRequestError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
)

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=settings.keycloak_auth_url,
    tokenUrl=settings.keycloak_token_url,
    auto_error=False,
)
bearer_scheme = HTTPBearer(auto_error=False)


def raise_http_error(exc: AppError) -> NoReturn:
    if isinstance(exc, BadRequestError):
        code = status.HTTP_400_BAD_REQUEST
    elif isinstance(exc, UnauthorizedError):
        code = status.HTTP_401_UNAUTHORIZED
    elif isinstance(exc, ForbiddenError):
        code = status.HTTP_403_FORBIDDEN
    elif isinstance(exc, NotFoundError):
        code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, ConflictError):
        code = status.HTTP_409_CONFLICT
    else:
        code = status.HTTP_400_BAD_REQUEST
    raise HTTPException(status_code=code, detail=exc.detail) from exc


def get_current_user(
    db: Session = Depends(get_db),
    oauth_token: str | None = Depends(oauth2_scheme),
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    x_user_id: int | None = Header(default=None, alias="X-User-Id"),
) -> User:
    repo = UserRepository(db)

    raw_token = oauth_token or (credentials.credentials if credentials is not None else None)
    if raw_token is not None:
        identity = verify_keycloak_token(raw_token)
        if identity is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Жарамсыз немесе мерзімі өткен токен",
            )
        role = extract_role(identity)
        return repo.sync(identity, role)

    if x_user_id is not None:
        user = repo.get(x_user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пайдаланушы табылмады",
            )
        return user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Аутентификация қажет",
    )
