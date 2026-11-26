from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_role
from app.models.user import User
from app.schemas.user import UserRead
from app.services.user_service import UserService

router = APIRouter(prefix="/api/users", tags=["Users"])
admin_only = require_role("admin")


@router.get("", response_model=list[UserRead])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only),
) -> list[UserRead]:
    users = UserService(db).list_users(current_user)
    return [UserRead.model_validate(u) for u in users]


@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only),
) -> UserRead:
    user = UserService(db).get_user(user_id, current_user)
    return UserRead.model_validate(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only),
) -> Response:
    UserService(db).delete_user(user_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
