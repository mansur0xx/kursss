from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.attempt import Attempt
    from app.models.question import Question
    from app.models.user import User


class Quiz(Base):
    __tablename__ = "quizzes"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    topic: Mapped[str] = mapped_column(String(120), default="")
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    owner: Mapped["User"] = relationship(back_populates="quizzes")
    questions: Mapped[list["Question"]] = relationship(
        back_populates="quiz", cascade="all, delete-orphan"
    )
    attempts: Mapped[list["Attempt"]] = relationship(
        back_populates="quiz", cascade="all, delete-orphan"
    )
