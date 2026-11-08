from typing import Annotated
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.core.security import AuthenticatedUser, get_current_user, require_roles
from app.llm.client import ollama_client

router = APIRouter()


class GenerateTestRequest(BaseModel):
    topic: str
    count: int = 5


class GenerateTestResponse(BaseModel):
    topic: str
    result: str


class ExplainRequest(BaseModel):
    question: str
    student_answer: str


class ExplainResponse(BaseModel):
    explanation: str


class ChatMessageRequest(BaseModel):
    message: str


class ChatMessageResponse(BaseModel):
    reply: str


@router.post("/generate-test", response_model=GenerateTestResponse)
async def generate_test(
    request: GenerateTestRequest,
    current_user: Annotated[AuthenticatedUser, Depends(require_roles(["teacher", "admin"]))]
):
    """
    Тек Мұғалімдер үшін: Ollama арқылы тақырып бойынша тест сұрақтарын генерациялау.
    """
    result = await ollama_client.generate_test_questions(topic=request.topic, count=request.count)
    return GenerateTestResponse(topic=request.topic, result=result)


@router.post("/explain", response_model=ExplainResponse)
async def explain_mistake(
    request: ExplainRequest,
    current_user: Annotated[AuthenticatedUser, Depends(require_roles(["student"]))]
):
    """
    Тек Студенттер үшін: Ollama арқылы қатені талдау және AI-менторлық түсініктеме алу.
    """
    explanation = await ollama_client.evaluate_answer(
        question=request.question,
        student_answer=request.student_answer
    )
    return ExplainResponse(explanation=explanation)


@router.post("/chat", response_model=ChatMessageResponse)
async def chat_with_ai(
    request: ChatMessageRequest,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)]
):
    """
    Барлық пайдаланушылар үшін: Жылжымалы Ollama AI-менторымен тікелей сөйлесу.
    """
    system_prompt = (
        "Сен EduPlatform жүйесінің ақылды AI-көмекшісісің. Студенттерге Python, FastAPI, Next.js, "
        "SQLAlchemy және алгоритмдер бойынша нақты, сыпайы әрі қазақ тілінде түсініктеме бересің. "
        f"Пайдаланушы сұрағы: {request.message}"
    )
    try:
        reply = await ollama_client.generate_completion(system_prompt)
    except Exception as e:
        reply = (
            f"Сәлеметсіз бе! Мен EduPlatform AI көмекшісімін. Қазіргі уақытта Ollama жергілікті контейнері "
            f"іске қосылуды күтуде (docker compose up -d). Сұрағыңыз: '{request.message}'. Бағдарламалау бойынша қандай көмек қажет?"
        )
    return ChatMessageResponse(reply=reply)
