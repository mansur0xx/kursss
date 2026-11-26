from fastapi import APIRouter, Depends

from app.models.user import User
from app.routers.deps import get_current_user
from app.schemas.user import UserRead

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.get("/me", response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(current_user)
