from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AttemptCreate(BaseModel):
    answers: list[int] = Field(..., min_length=1)


class AttemptRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    quiz_id: int
    student_id: int
    answers: list[int]
    score: int
    total: int
    submitted_at: datetime


class QuizResultItem(BaseModel):
    attempt_id: int
    student_id: int
    student_name: str
    student_email: str
    score: int
    total: int
    percent: float
    submitted_at: datetime


class QuizResultsSummary(BaseModel):
    quiz_id: int
    quiz_title: str
    total_attempts: int
    average_score: float
    average_percent: float
    results: list[QuizResultItem]
