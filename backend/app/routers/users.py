from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.routers.deps import get_current_user, raise_http_error
from app.schemas.user import UserRead, UserUpdate
from app.services.exceptions import AppError
from app.services.user_service import UserService

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("", response_model=list[UserRead])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[UserRead]:
    service = UserService(db)
    try:
        users = service.list_users(current_user)
        return [UserRead.model_validate(u) for u in users]
    except AppError as exc:
        raise_http_error(exc)


@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserRead:
    service = UserService(db)
    try:
        user = service.get_user(user_id, current_user)
        return UserRead.model_validate(user)
    except AppError as exc:
        raise_http_error(exc)


@router.patch("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserRead:
    service = UserService(db)
    try:
        user = service.update_user(user_id, payload, current_user)
        return UserRead.model_validate(user)
    except AppError as exc:
        raise_http_error(exc)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    service = UserService(db)
    try:
        service.delete_user(user_id, current_user)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except AppError as exc:
        raise_http_error(exc)
