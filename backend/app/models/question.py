from typing import TYPE_CHECKING

from sqlalchemy import JSON, CheckConstraint, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.quiz import Quiz


class Question(Base):
    __tablename__ = "questions"
    __table_args__ = (
        CheckConstraint(
            "correct_index >= 0",
            name="ck_questions_correct_index",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    quiz_id: Mapped[int] = mapped_column(
        ForeignKey("quizzes.id", ondelete="CASCADE"),
        index=True,
    )
    prompt: Mapped[str] = mapped_column(Text)
    options: Mapped[list[str]] = mapped_column(JSON)
    correct_index: Mapped[int] = mapped_column(Integer)

    quiz: Mapped["Quiz"] = relationship(back_populates="questions")
