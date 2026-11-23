import csv
import io

from sqlalchemy.orm import Session

from app.models.attempt import Attempt
from app.models.user import User
from app.repositories.attempt_repository import AttemptRepository
from app.repositories.question_repository import QuestionRepository
from app.repositories.quiz_repository import QuizRepository
from app.repositories.user_repository import UserRepository
from app.schemas.attempt import AttemptCreate, QuizResultItem, QuizResultsSummary
from app.services.exceptions import BadRequestError, ForbiddenError, NotFoundError


class AttemptService:
    def __init__(self, db: Session) -> None:
        self.repo = AttemptRepository(db)
        self.quiz_repo = QuizRepository(db)
        self.question_repo = QuestionRepository(db)
        self.user_repo = UserRepository(db)

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

    def get_quiz_results(self, quiz_id: int, current_user: User) -> QuizResultsSummary:
        if current_user.role not in ("teacher", "admin"):
            raise ForbiddenError("Тек мұғалім немесе әкімші нәтижелер журналын көре алады")
        quiz = self.quiz_repo.get(quiz_id)
        if quiz is None:
            raise NotFoundError("Тест табылмады")
        if current_user.role == "teacher" and quiz.owner_id != current_user.id:
            raise ForbiddenError("Бөтен тесттің нәтижелерін көруге болмайды")

        attempts = self.repo.list_by_quiz(quiz.id)
        items: list[QuizResultItem] = []
        for att in attempts:
            student = self.user_repo.get(att.student_id)
            percent = round((att.score / att.total) * 100.0, 2) if att.total > 0 else 0.0
            items.append(
                QuizResultItem(
                    attempt_id=att.id,
                    student_id=att.student_id,
                    student_name=student.full_name if student else f"User #{att.student_id}",
                    student_email=student.email if student else "",
                    score=att.score,
                    total=att.total,
                    percent=percent,
                    submitted_at=att.submitted_at,
                )
            )

        total_attempts = len(items)
        avg_score = round(sum(i.score for i in items) / total_attempts, 2) if total_attempts else 0.0
        avg_percent = (
            round(sum(i.percent for i in items) / total_attempts, 2) if total_attempts else 0.0
        )

        return QuizResultsSummary(
            quiz_id=quiz.id,
            quiz_title=quiz.title,
            total_attempts=total_attempts,
            average_score=avg_score,
            average_percent=avg_percent,
            results=items,
        )

    def export_quiz_results_csv(self, quiz_id: int, current_user: User) -> str:
        summary = self.get_quiz_results(quiz_id, current_user)
        buf = io.StringIO()
        buf.write("\ufeff")  # UTF-8 BOM for Excel Cyrillic/Kazakh support
        writer = csv.writer(buf)
        writer.writerow(
            ["attempt_id", "student_name", "student_email", "score", "total", "percent", "submitted_at"]
        )
        for row in summary.results:
            writer.writerow(
                [
                    row.attempt_id,
                    row.student_name,
                    row.student_email,
                    row.score,
                    row.total,
                    row.percent,
                    row.submitted_at.isoformat(),
                ]
            )
        return buf.getvalue()
