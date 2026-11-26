from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_role
from app.models.user import User
from app.schemas.question import QuestionCreate, QuestionRead, QuestionUpdate
from app.services.question_service import QuestionService

router = APIRouter(prefix="/api", tags=["Questions"])
teacher_or_admin = require_role("teacher", "admin")


@router.post(
    "/quizzes/{quiz_id}/questions",
    response_model=QuestionRead,
    status_code=status.HTTP_201_CREATED,
)
def add_question(
    quiz_id: int,
    payload: QuestionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(teacher_or_admin),
) -> QuestionRead:
    question = QuestionService(db).add_question(quiz_id, payload, current_user)
    return QuestionRead.model_validate(question)


@router.patch("/questions/{question_id}", response_model=QuestionRead)
def update_question(
    question_id: int,
    payload: QuestionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(teacher_or_admin),
) -> QuestionRead:
    question = QuestionService(db).update_question(question_id, payload, current_user)
    return QuestionRead.model_validate(question)


@router.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(teacher_or_admin),
) -> Response:
    QuestionService(db).delete_question(question_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
