from sqlalchemy.orm import Session

from app.models.quiz import Quiz
from app.models.user import User
from app.repositories.question_repository import QuestionRepository
from app.repositories.quiz_repository import QuizRepository
from app.schemas.quiz import QuizCreate, QuizUpdate
from app.services.exceptions import BadRequestError, ForbiddenError, NotFoundError


class QuizService:
    def __init__(self, db: Session) -> None:
        self.repo = QuizRepository(db)
        self.question_repo = QuestionRepository(db)

    def list_quizzes(self, current_user: User) -> list[Quiz]:
        if current_user.role == "admin":
            return self.repo.list()
        if current_user.role == "teacher":
            return self.repo.list(owner_id=current_user.id, published_only=True)
        return self.repo.list(published_only=True)

    def create_quiz(self, payload: QuizCreate, current_user: User) -> Quiz:
        if current_user.role not in ("teacher", "admin"):
            raise ForbiddenError("Тек мұғалім немесе әкімші тест құра алады")
        return self.repo.create(
            title=payload.title,
            topic=payload.topic,
            owner_id=current_user.id,
        )

    def get_quiz(self, quiz_id: int, current_user: User) -> Quiz:
        quiz = self.repo.get(quiz_id)
        if quiz is None:
            raise NotFoundError("Тест табылмады")
        if current_user.role == "student" and not quiz.is_published:
            raise NotFoundError("Тест табылмады")
        return quiz

    def update_quiz(self, quiz_id: int, payload: QuizUpdate, current_user: User) -> Quiz:
        if current_user.role not in ("teacher", "admin"):
            raise ForbiddenError("Рұқсат жоқ")
        quiz = self.repo.get(quiz_id)
        if quiz is None:
            raise NotFoundError("Тест табылмады")
        if current_user.role == "teacher" and quiz.owner_id != current_user.id:
            raise ForbiddenError("Бөтен тестті өзгертуге болмайды")
        if payload.title is not None:
            quiz.title = payload.title
        if payload.topic is not None:
            quiz.topic = payload.topic
        return self.repo.save(quiz)

    def delete_quiz(self, quiz_id: int, current_user: User) -> None:
        if current_user.role not in ("teacher", "admin"):
            raise ForbiddenError("Рұқсат жоқ")
        quiz = self.repo.get(quiz_id)
        if quiz is None:
            raise NotFoundError("Тест табылмады")
        if current_user.role == "teacher" and quiz.owner_id != current_user.id:
            raise ForbiddenError("Бөтен тестті өшіруге болмайды")
        self.repo.delete(quiz)

    def publish_quiz(self, quiz_id: int, current_user: User) -> Quiz:
        if current_user.role not in ("teacher", "admin"):
            raise ForbiddenError("Рұқсат жоқ")
        quiz = self.repo.get(quiz_id)
        if quiz is None:
            raise NotFoundError("Тест табылмады")
        if current_user.role == "teacher" and quiz.owner_id != current_user.id:
            raise ForbiddenError("Бөтен тестті жариялауға болмайды")
        questions = self.question_repo.list_by_quiz(quiz.id)
        if not questions:
            raise BadRequestError("Сұрағы жоқ тестті жариялауға болмайды")
        quiz.is_published = True
        return self.repo.save(quiz)
