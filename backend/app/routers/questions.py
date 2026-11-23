from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.routers.deps import get_current_user, raise_http_error
from app.schemas.question import QuestionCreate, QuestionRead, QuestionUpdate
from app.services.exceptions import AppError
from app.services.question_service import QuestionService

router = APIRouter(prefix="/api", tags=["Questions"])


@router.post(
    "/quizzes/{quiz_id}/questions",
    response_model=QuestionRead,
    status_code=status.HTTP_201_CREATED,
)
def add_question(
    quiz_id: int,
    payload: QuestionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QuestionRead:
    service = QuestionService(db)
    try:
        question = service.add_question(quiz_id, payload, current_user)
        return QuestionRead.model_validate(question)
    except AppError as exc:
        raise_http_error(exc)


@router.patch("/questions/{question_id}", response_model=QuestionRead)
def update_question(
    question_id: int,
    payload: QuestionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QuestionRead:
    service = QuestionService(db)
    try:
        question = service.update_question(question_id, payload, current_user)
        return QuestionRead.model_validate(question)
    except AppError as exc:
        raise_http_error(exc)


@router.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    service = QuestionService(db)
    try:
        service.delete_question(question_id, current_user)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except AppError as exc:
        raise_http_error(exc)
