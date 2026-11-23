from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.question import QuestionRead, QuestionStudentRead


class QuizCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    topic: str = Field(default="", max_length=120)


class QuizUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    topic: str | None = Field(default=None, max_length=120)


class QuizRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    topic: str
    owner_id: int
    is_published: bool
    created_at: datetime


class QuizDetailRead(QuizRead):
    questions: list[QuestionRead] = Field(default_factory=list)


class QuizStudentDetailRead(QuizRead):
    questions: list[QuestionStudentRead] = Field(default_factory=list)
