from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.routers.deps import get_current_user, raise_http_error
from app.schemas.attempt import AttemptCreate, AttemptRead, QuizResultsSummary
from app.services.attempt_service import AttemptService
from app.services.exceptions import AppError

router = APIRouter(prefix="/api", tags=["Attempts & Results"])


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


@router.get("/quizzes/{quiz_id}/results", response_model=QuizResultsSummary)
def get_quiz_results(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QuizResultsSummary:
    service = AttemptService(db)
    try:
        return service.get_quiz_results(quiz_id, current_user)
    except AppError as exc:
        raise_http_error(exc)


@router.get("/quizzes/{quiz_id}/results/export")
def export_quiz_results_csv(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    service = AttemptService(db)
    try:
        csv_content = service.export_quiz_results_csv(quiz_id, current_user)
        return Response(
            content=csv_content,
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="quiz_{quiz_id}_results.csv"'},
        )
    except AppError as exc:
        raise_http_error(exc)
