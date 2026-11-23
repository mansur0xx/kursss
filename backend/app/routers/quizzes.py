from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.routers.deps import get_current_user, raise_http_error
from app.schemas.quiz import (
    QuizCreate,
    QuizDetailRead,
    QuizRead,
    QuizStudentDetailRead,
    QuizUpdate,
)
from app.services.exceptions import AppError
from app.services.quiz_service import QuizService

router = APIRouter(prefix="/api/quizzes", tags=["Quizzes"])


@router.get("", response_model=list[QuizRead])
def list_quizzes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[QuizRead]:
    service = QuizService(db)
    try:
        quizzes = service.list_quizzes(current_user)
        return [QuizRead.model_validate(q) for q in quizzes]
    except AppError as exc:
        raise_http_error(exc)


@router.post("", response_model=QuizRead, status_code=status.HTTP_201_CREATED)
def create_quiz(
    payload: QuizCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QuizRead:
    service = QuizService(db)
    try:
        quiz = service.create_quiz(payload, current_user)
        return QuizRead.model_validate(quiz)
    except AppError as exc:
        raise_http_error(exc)


@router.get("/{quiz_id}", response_model=QuizDetailRead | QuizStudentDetailRead)
def get_quiz(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QuizDetailRead | QuizStudentDetailRead:
    service = QuizService(db)
    try:
        quiz = service.get_quiz(quiz_id, current_user)
        if current_user.role == "student":
            return QuizStudentDetailRead.model_validate(quiz)
        return QuizDetailRead.model_validate(quiz)
    except AppError as exc:
        raise_http_error(exc)


@router.patch("/{quiz_id}", response_model=QuizRead)
def update_quiz(
    quiz_id: int,
    payload: QuizUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QuizRead:
    service = QuizService(db)
    try:
        quiz = service.update_quiz(quiz_id, payload, current_user)
        return QuizRead.model_validate(quiz)
    except AppError as exc:
        raise_http_error(exc)


@router.delete("/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quiz(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    service = QuizService(db)
    try:
        service.delete_quiz(quiz_id, current_user)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except AppError as exc:
        raise_http_error(exc)


@router.post("/{quiz_id}/publish", response_model=QuizRead)
def publish_quiz(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QuizRead:
    service = QuizService(db)
    try:
        quiz = service.publish_quiz(quiz_id, current_user)
        return QuizRead.model_validate(quiz)
    except AppError as exc:
        raise_http_error(exc)
