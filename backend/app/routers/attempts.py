from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_role
from app.models.user import User
from app.schemas.attempt import AttemptCreate, AttemptRead, QuizResultsSummary
from app.services.attempt_service import AttemptService

router = APIRouter(prefix="/api", tags=["Attempts & Results"])
student_only = require_role("student")
teacher_or_admin = require_role("teacher", "admin")


@router.post(
    "/quizzes/{quiz_id}/attempts",
    response_model=AttemptRead,
    status_code=status.HTTP_201_CREATED,
)
def submit_attempt(
    quiz_id: int,
    payload: AttemptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(student_only),
) -> AttemptRead:
    attempt = AttemptService(db).submit_attempt(quiz_id, payload, current_user)
    return AttemptRead.model_validate(attempt)


@router.get("/attempts/me", response_model=list[AttemptRead])
def list_my_attempts(
    db: Session = Depends(get_db),
    current_user: User = Depends(student_only),
) -> list[AttemptRead]:
    attempts = AttemptService(db).list_my_attempts(current_user)
    return [AttemptRead.model_validate(a) for a in attempts]


@router.get("/quizzes/{quiz_id}/results", response_model=QuizResultsSummary)
def get_quiz_results(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(teacher_or_admin),
) -> QuizResultsSummary:
    return AttemptService(db).get_quiz_results(quiz_id, current_user)


@router.get("/quizzes/{quiz_id}/results/export")
def export_quiz_results_csv(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(teacher_or_admin),
) -> Response:
    csv_content = AttemptService(db).export_quiz_results_csv(quiz_id, current_user)
    return Response(
        content=csv_content,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="quiz_{quiz_id}_results.csv"'},
    )
