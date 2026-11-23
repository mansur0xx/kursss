from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.routers.deps import get_current_user, raise_http_error
from app.schemas.attempt import AttemptCreate, AttemptRead
from app.services.attempt_service import AttemptService
from app.services.exceptions import AppError

router = APIRouter(prefix="/api", tags=["Attempts"])


@router.post(
    "/quizzes/{quiz_id}/attempts",
    response_model=AttemptRead,
    status_code=status.HTTP_201_CREATED,
)
def submit_attempt(
    quiz_id: int,
    payload: AttemptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AttemptRead:
    service = AttemptService(db)
    try:
        attempt = service.submit_attempt(quiz_id, payload, current_user)
        return AttemptRead.model_validate(attempt)
    except AppError as exc:
        raise_http_error(exc)


@router.get("/attempts/me", response_model=list[AttemptRead])
def list_my_attempts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[AttemptRead]:
    service = AttemptService(db)
    try:
        attempts = service.list_my_attempts(current_user)
        return [AttemptRead.model_validate(a) for a in attempts]
    except AppError as exc:
        raise_http_error(exc)
