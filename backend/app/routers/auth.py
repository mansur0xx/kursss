from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.routers.deps import raise_http_error
from app.schemas.user import UserLogin, UserRead, UserRegister
from app.services.auth_service import AuthService
from app.services.exceptions import AppError

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)) -> UserRead:
    service = AuthService(db)
    try:
        user = service.register(payload)
        return UserRead.model_validate(user)
    except AppError as exc:
        raise_http_error(exc)


@router.post("/login", response_model=UserRead, status_code=status.HTTP_200_OK)
def login(payload: UserLogin, db: Session = Depends(get_db)) -> UserRead:
    service = AuthService(db)
    try:
        user = service.login(payload)
        return UserRead.model_validate(user)
    except AppError as exc:
        raise_http_error(exc)
