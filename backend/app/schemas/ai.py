from pydantic import BaseModel, Field

from app.schemas.question import QuestionRead


class GenerateQuestionsRequest(BaseModel):
    topic: str = Field(..., min_length=2, max_length=200)
    count: int = Field(default=3, ge=1, le=10)


class GenerateQuestionsResponse(BaseModel):
    quiz_id: int
    source: str
    questions: list[QuestionRead]
