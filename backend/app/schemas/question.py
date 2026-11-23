from pydantic import BaseModel, ConfigDict, Field


class QuestionCreate(BaseModel):
    prompt: str = Field(..., min_length=1)
    options: list[str] = Field(..., min_length=2, max_length=6)
    correct_index: int = Field(..., ge=0)


class QuestionUpdate(BaseModel):
    prompt: str | None = Field(default=None, min_length=1)
    options: list[str] | None = Field(default=None, min_length=2, max_length=6)
    correct_index: int | None = Field(default=None, ge=0)


class QuestionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    quiz_id: int
    prompt: str
    options: list[str]
    correct_index: int


class QuestionStudentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    quiz_id: int
    prompt: str
    options: list[str]
