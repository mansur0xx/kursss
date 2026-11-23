from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.routers.deps import get_current_user, raise_http_error
from app.schemas.ai import GenerateQuestionsRequest, GenerateQuestionsResponse
from app.schemas.question import QuestionRead
from app.services.ai_service import AIService
from app.services.exceptions import AppError

router = APIRouter(prefix="/api", tags=["AI"])


@router.post(
    "/quizzes/{quiz_id}/generate-questions",
    response_model=GenerateQuestionsResponse,
    status_code=status.HTTP_201_CREATED,
)
def generate_questions(
    quiz_id: int,
    payload: GenerateQuestionsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> GenerateQuestionsResponse:
    service = AIService(db)
    try:
        source, questions = service.generate_questions_for_quiz(quiz_id, payload, current_user)
        return GenerateQuestionsResponse(
            quiz_id=quiz_id,
            source=source,
            questions=[QuestionRead.model_validate(q) for q in questions],
        )
    except AppError as exc:
        raise_http_error(exc)
