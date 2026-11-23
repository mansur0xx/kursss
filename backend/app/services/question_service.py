from sqlalchemy.orm import Session

from app.models.question import Question
from app.models.user import User
from app.repositories.question_repository import QuestionRepository
from app.repositories.quiz_repository import QuizRepository
from app.schemas.question import QuestionCreate, QuestionUpdate
from app.services.exceptions import BadRequestError, ForbiddenError, NotFoundError


class QuestionService:
    def __init__(self, db: Session) -> None:
        self.repo = QuestionRepository(db)
        self.quiz_repo = QuizRepository(db)

    def add_question(
        self,
        quiz_id: int,
        payload: QuestionCreate,
        current_user: User,
    ) -> Question:
        if current_user.role not in ("teacher", "admin"):
            raise ForbiddenError("Рұқсат жоқ")
        quiz = self.quiz_repo.get(quiz_id)
        if quiz is None:
            raise NotFoundError("Тест табылмады")
        if current_user.role == "teacher" and quiz.owner_id != current_user.id:
            raise ForbiddenError("Бөтен тестке сұрақ қосуға болмайды")
        if quiz.is_published:
            raise BadRequestError("Жарияланған тестке сұрақ қосуға болмайды")
        if payload.correct_index >= len(payload.options):
            raise BadRequestError("correct_index нұсқалар санынан аспауы тиіс")
        return self.repo.create(
            quiz_id=quiz.id,
            prompt=payload.prompt,
            options=payload.options,
            correct_index=payload.correct_index,
        )

    def update_question(
        self,
        question_id: int,
        payload: QuestionUpdate,
        current_user: User,
    ) -> Question:
        if current_user.role not in ("teacher", "admin"):
            raise ForbiddenError("Рұқсат жоқ")
        question = self.repo.get(question_id)
        if question is None:
            raise NotFoundError("Сұрақ табылмады")
        quiz = self.quiz_repo.get(question.quiz_id)
        if quiz is None:
            raise NotFoundError("Тест табылмады")
        if current_user.role == "teacher" and quiz.owner_id != current_user.id:
            raise ForbiddenError("Бөтен тесттің сұрағын өзгертуге болмайды")
        if quiz.is_published:
            raise BadRequestError("Жарияланған тесттің сұрағын өзгертуге болмайды")

        new_options = payload.options if payload.options is not None else question.options
        new_correct_index = (
            payload.correct_index
            if payload.correct_index is not None
            else question.correct_index
        )
        if new_correct_index >= len(new_options):
            raise BadRequestError("correct_index нұсқалар санынан аспауы тиіс")

        if payload.prompt is not None:
            question.prompt = payload.prompt
        if payload.options is not None:
            question.options = payload.options
        if payload.correct_index is not None:
            question.correct_index = payload.correct_index
        return self.repo.save(question)

    def delete_question(self, question_id: int, current_user: User) -> None:
        if current_user.role not in ("teacher", "admin"):
            raise ForbiddenError("Рұқсат жоқ")
        question = self.repo.get(question_id)
        if question is None:
            raise NotFoundError("Сұрақ табылмады")
        quiz = self.quiz_repo.get(question.quiz_id)
        if quiz is None:
            raise NotFoundError("Тест табылмады")
        if current_user.role == "teacher" and quiz.owner_id != current_user.id:
            raise ForbiddenError("Бөтен тесттің сұрағын өшіруге болмайды")
        if quiz.is_published:
            raise BadRequestError("Жарияланған тесттің сұрағын өшіруге болмайды")
        self.repo.delete(question)
