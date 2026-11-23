from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.attempt import Attempt


class AttemptRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_by_student(self, student_id: int) -> list[Attempt]:
        stmt = select(Attempt).where(Attempt.student_id == student_id).order_by(Attempt.id)
        return list(self.db.scalars(stmt).all())

    def get(self, attempt_id: int) -> Attempt | None:
        return self.db.get(Attempt, attempt_id)

    def create(
        self,
        *,
        quiz_id: int,
        student_id: int,
        answers: list[int],
        score: int,
        total: int,
    ) -> Attempt:
        attempt = Attempt(
            quiz_id=quiz_id,
            student_id=student_id,
            answers=answers,
            score=score,
            total=total,
        )
        self.db.add(attempt)
        self.db.commit()
        self.db.refresh(attempt)
        return attempt
