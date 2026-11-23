from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.quiz import Quiz


class QuizRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self, owner_id: int | None = None, published_only: bool = False) -> list[Quiz]:
        stmt = select(Quiz).order_by(Quiz.id)
        if published_only and owner_id is not None:
            stmt = stmt.where(or_(Quiz.is_published.is_(True), Quiz.owner_id == owner_id))
        elif published_only:
            stmt = stmt.where(Quiz.is_published.is_(True))
        elif owner_id is not None:
            stmt = stmt.where(Quiz.owner_id == owner_id)
        return list(self.db.scalars(stmt).all())

    def get(self, quiz_id: int) -> Quiz | None:
        return self.db.get(Quiz, quiz_id)

    def create(self, *, title: str, topic: str, owner_id: int) -> Quiz:
        quiz = Quiz(title=title, topic=topic, owner_id=owner_id)
        self.db.add(quiz)
        self.db.commit()
        self.db.refresh(quiz)
        return quiz

    def save(self, quiz: Quiz) -> Quiz:
        self.db.add(quiz)
        self.db.commit()
        self.db.refresh(quiz)
        return quiz

    def delete(self, quiz: Quiz) -> None:
        self.db.delete(quiz)
        self.db.commit()
