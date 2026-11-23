import json
from typing import Any

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.question import Question
from app.models.user import User
from app.repositories.question_repository import QuestionRepository
from app.repositories.quiz_repository import QuizRepository
from app.schemas.ai import GenerateQuestionsRequest
from app.services.exceptions import BadRequestError, ForbiddenError, NotFoundError


def _build_fallback_questions(topic: str, count: int) -> list[dict[str, Any]]:
    templates = [
        {
            "prompt": f"«{topic}» тақырыбының негізгі мақсаты қандай?",
            "options": [
                f"{topic} ұғымдарын жүйелі қолдану",
                "Деректерді өшіру",
                "Қосылымды тоқтату",
                "Тек визуалды безендіру",
            ],
            "correct_index": 0,
        },
        {
            "prompt": f"«{topic}» бойынша тәжірибеде қай тәсіл ең дұрыс саналады?",
            "options": [
                "Тексерусіз іске қосу",
                "Құрылымдалған және валидацияланған тәсіл",
                "Құпия кілттерді кодта сақтау",
                "Барлық қателерді елемеу",
            ],
            "correct_index": 1,
        },
        {
            "prompt": f"«{topic}» қолдану кезінде қауіпсіздік пен сапаны не қамтамасыз етеді?",
            "options": [
                "Қолмен көшіру",
                "Логтарды өшіру",
                "Автоматты тестілеу және стандарттарды сақтау",
                "Ешқандай шектеу қоймау",
            ],
            "correct_index": 2,
        },
    ]
    result: list[dict[str, Any]] = []
    for idx in range(count):
        base = templates[idx % len(templates)]
        suffix = f" (#{idx + 1})" if idx >= len(templates) else ""
        result.append(
            {
                "prompt": f"{base['prompt']}{suffix}",
                "options": list(base["options"]),
                "correct_index": int(base["correct_index"]),
            }
        )
    return result


def _try_ollama_questions(topic: str, count: int) -> list[dict[str, Any]] | None:
    prompt = (
        f"Generate exactly {count} multiple-choice quiz questions in Kazakh about '{topic}'. "
        "Return ONLY a valid JSON array of objects with keys: "
        '"prompt" (string), "options" (array of 4 strings), "correct_index" (integer 0-3).'
    )
    try:
        with httpx.Client(timeout=4.0) as client:
            resp = client.post(
                f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/generate",
                json={
                    "model": settings.OLLAMA_DEFAULT_MODEL,
                    "prompt": prompt,
                    "stream": False,
                },
            )
            resp.raise_for_status()
            raw = resp.json().get("response", "").strip()
            start = raw.find("[")
            end = raw.rfind("]")
            if start == -1 or end == -1:
                return None
            parsed = json.loads(raw[start : end + 1])
            if not isinstance(parsed, list) or not parsed:
                return None
            valid: list[dict[str, Any]] = []
            for item in parsed[:count]:
                if (
                    isinstance(item, dict)
                    and isinstance(item.get("prompt"), str)
                    and isinstance(item.get("options"), list)
                    and 2 <= len(item["options"]) <= 6
                    and isinstance(item.get("correct_index"), int)
                    and 0 <= item["correct_index"] < len(item["options"])
                ):
                    valid.append(
                        {
                            "prompt": item["prompt"].strip(),
                            "options": [str(o) for o in item["options"]],
                            "correct_index": item["correct_index"],
                        }
                    )
            return valid if valid else None
    except (httpx.HTTPError, ValueError, KeyError):
        return None


class AIService:
    def __init__(self, db: Session) -> None:
        self.quiz_repo = QuizRepository(db)
        self.question_repo = QuestionRepository(db)

    def generate_questions_for_quiz(
        self,
        quiz_id: int,
        payload: GenerateQuestionsRequest,
        current_user: User,
    ) -> tuple[str, list[Question]]:
        if current_user.role not in ("teacher", "admin"):
            raise ForbiddenError("Тек мұғалім немесе әкімші AI сұрақтарын генерациялай алады")
        quiz = self.quiz_repo.get(quiz_id)
        if quiz is None:
            raise NotFoundError("Тест табылмады")
        if current_user.role == "teacher" and quiz.owner_id != current_user.id:
            raise ForbiddenError("Бөтен тестке сұрақ генерациялауға болмайды")
        if quiz.is_published:
            raise BadRequestError("Жарияланған тестке сұрақ қосуға болмайды")

        generated = _try_ollama_questions(payload.topic, payload.count)
        if generated is not None:
            source = "ollama"
        else:
            source = "fallback"
            generated = _build_fallback_questions(payload.topic, payload.count)

        saved: list[Question] = []
        for item in generated:
            q = self.question_repo.create(
                quiz_id=quiz.id,
                prompt=item["prompt"],
                options=item["options"],
                correct_index=item["correct_index"],
            )
            saved.append(q)
        return source, saved
