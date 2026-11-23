from sqlalchemy.orm import Session

from app.models.attempt import Attempt
from app.models.user import User
from app.repositories.attempt_repository import AttemptRepository
from app.repositories.question_repository import QuestionRepository
from app.repositories.quiz_repository import QuizRepository
from app.schemas.attempt import AttemptCreate
from app.services.exceptions import BadRequestError, ForbiddenError, NotFoundError


class AttemptService:
    def __init__(self, db: Session) -> None:
        self.repo = AttemptRepository(db)
        self.quiz_repo = QuizRepository(db)
        self.question_repo = QuestionRepository(db)

    def submit_attempt(
        self,
        quiz_id: int,
        payload: AttemptCreate,
        current_user: User,
    ) -> Attempt:
        if current_user.role != "student":
            raise ForbiddenError("Тек студент тест тапсыра алады")
        quiz = self.quiz_repo.get(quiz_id)
        if quiz is None:
            raise NotFoundError("Тест табылмады")
        if not quiz.is_published:
            raise BadRequestError("Жарияланбаған тестті тапсыруға болмайды")
        questions = self.question_repo.list_by_quiz(quiz.id)
        if len(payload.answers) != len(questions):
            raise BadRequestError("Жауаптар саны сұрақтар санына сәйкес келмейді")
        score = sum(
            1
            for q, ans in zip(questions, payload.answers, strict=False)
            if q.correct_index == ans
        )
        return self.repo.create(
            quiz_id=quiz.id,
            student_id=current_user.id,
            answers=payload.answers,
            score=score,
            total=len(questions),
        )

    def list_my_attempts(self, current_user: User) -> list[Attempt]:
        if current_user.role != "student":
            raise ForbiddenError("Тек студент өз талпыныстарын көре алады")
        return self.repo.list_by_student(current_user.id)
