from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, CheckConstraint, DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.quiz import Quiz
    from app.models.user import User


class Attempt(Base):
    __tablename__ = "attempts"
    __table_args__ = (
        CheckConstraint(
            "score >= 0",
            name="ck_attempts_score",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    quiz_id: Mapped[int] = mapped_column(
        ForeignKey("quizzes.id", ondelete="CASCADE"),
        index=True,
    )
    student_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    answers: Mapped[list[int]] = mapped_column(JSON)
    score: Mapped[int] = mapped_column(Integer, default=0)
    total: Mapped[int] = mapped_column(Integer, default=0)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    quiz: Mapped["Quiz"] = relationship(back_populates="attempts")
    student: Mapped["User"] = relationship(back_populates="attempts")
