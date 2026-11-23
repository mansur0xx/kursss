from typing import NoReturn

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.auth_service import get_last_authenticated_user_id
from app.services.exceptions import (
    AppError,
    BadRequestError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
)


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
    x_user_id: int | None = Header(default=None, alias="X-User-Id"),
    x_user_role: str | None = Header(default=None, alias="X-User-Role"),
) -> User:
    repo = UserRepository(db)

    if x_user_id is not None:
        user = repo.get(x_user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пайдаланушы табылмады",
            )
        return user

    if x_user_role is not None:
        role = x_user_role.strip().lower()
        if role not in ("student", "teacher", "admin"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Жарамсыз рөл",
            )
        default_email = f"default_{role}@quizai.local"
        user = repo.get_by_email(default_email)
        if user is None:
            user = repo.create(
                email=default_email,
                full_name=f"Default {role.capitalize()}",
                role=role,
            )
        return user

    last_id = get_last_authenticated_user_id()
    if last_id is not None:
        user = repo.get(last_id)
        if user is not None:
            return user

    users = repo.list()
    if users:
        return users[0]

    return repo.create(
        email="default_teacher@quizai.local",
        full_name="Default Teacher",
        role="teacher",
    )
