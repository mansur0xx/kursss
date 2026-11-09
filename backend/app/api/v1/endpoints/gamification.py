from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import AuthenticatedUser, get_current_user
from app.db.session import get_db

router = APIRouter()

# DTO Модельдері
class SkillNode(BaseModel):
    id: str
    title: str
    description: str
    category: str
    xp_reward: int
    status: str  # "completed", "active", "locked"
    icon: str
    quiz_question: str | None = None
    quiz_options: list[str] | None = None
    correct_option_index: int | None = None


class LeaderboardEntry(BaseModel):
    rank: int
    user_id: str
    name: str
    avatar: str
    level: int
    xp: int
    streak_days: int
    league: str
    is_current_user: bool = False


class GamificationOverview(BaseModel):
    user_id: str
    level: int
    current_xp: int
    xp_to_next_level: int
    level_title: str
    streak_days: int
    today_completed: bool
    league: str
    weekly_rank: int
    daily_quests: list[dict[str, str | int | bool]]


# Тұрақты үлгілік мәліметтер (Mock data & logic for Skill Tree)
INITIAL_SKILL_NODES = [
    {
        "id": "node_1",
        "title": "Python негіздері мен синтаксисі",
        "description": "Айнымалылар, деректер типтері, циклдер мен шартты операторлар",
        "category": "Негіздер",
        "xp_reward": 100,
        "status": "completed",
        "icon": "🐍",
        "quiz_question": "Python-да тізімге (list) жаңа элемент қосу үшін қандай әдіс қолданылады?",
        "quiz_options": [".push()", ".append()", ".add()", ".insert_last()"],
        "correct_option_index": 1,
    },
    {
        "id": "node_2",
        "title": "Функциялар мен Модульдер",
        "description": "def, *args, **kwargs, lambda және модулдік архитектура",
        "category": "Негіздер",
        "xp_reward": 150,
        "status": "completed",
        "icon": "📦",
        "quiz_question": "Функциядағы кездейсоқ атаулы параметрлерді қабылдау үшін не қолданылады?",
        "quiz_options": ["*args", "**kwargs", "&params", "$props"],
        "correct_option_index": 1,
    },
    {
        "id": "node_3",
        "title": "FastAPI REST API негіздері",
        "description": "Pydantic модельдері, Path/Query параметрлері және APIRouter",
        "category": "Backend",
        "xp_reward": 200,
        "status": "completed",
        "icon": "⚡",
        "quiz_question": "FastAPI-де деректерді валидациялау және сериализациялау үшін қандай кітапхана қолданылады?",
        "quiz_options": ["Marshmallow", "Cerberus", "Pydantic", "Django Forms"],
        "correct_option_index": 2,
    },
    {
        "id": "node_4",
        "title": "PostgreSQL және SQLAlchemy 2.0 ORM",
        "description": "Асинхронды сессиялар, реляциялық байланыстар және Alembic миграциясы",
        "category": "Деректер қоры",
        "xp_reward": 250,
        "status": "active",
        "icon": "🐘",
        "quiz_question": "SQLAlchemy 2.0 нұсқасында сұраныс жасау үшін қандай синтаксис стандартты болып саналады?",
        "quiz_options": ["session.query()", "select() операторы", "db.find()", "raw_sql.execute()"],
        "correct_option_index": 1,
    },
    {
        "id": "node_5",
        "title": "Docker және Микросервистік орта",
        "description": "Dockerfile, Docker Compose, желілік байланыстар және порт баптаулары",
        "category": "DevOps",
        "xp_reward": 300,
        "status": "locked",
        "icon": "🐳",
        "quiz_question": "Бірнеше контейнерді бірге байланыстырып басқару үшін қандай құрал қолданылады?",
        "quiz_options": ["Docker Compose", "Docker Swarm", "Kubectl", "Systemd"],
        "correct_option_index": 0,
    },
    {
        "id": "node_6",
        "title": "Keycloak OIDC & RBAC Аутентификация",
        "description": "JWT токендер, Realm, рөлдерге бөлу (Student / Teacher / Admin)",
        "category": "Қауіпсіздік",
        "xp_reward": 350,
        "status": "locked",
        "icon": "🔐",
        "quiz_question": "OIDC токенінде пайдаланушының құқықтары мен рөлдері қай жерде сақталады?",
        "quiz_options": ["Header", "Payload / Claims", "Signature", "Cookie"],
        "correct_option_index": 1,
    },
    {
        "id": "node_7",
        "title": "Ollama және Жергілікті AI Интеграциясы (БОСС-ДЕҢГЕЙ)",
        "description": "Llama 3.2 жергілікті моделі, сұрақ генераторы және AI ментор көмекшісі",
        "category": "Жасанды Интеллект",
        "xp_reward": 500,
        "status": "locked",
        "icon": "👑",
        "quiz_question": "Ollama моделінен жауапты асинхронды түрде тарту үшін FastAPI-де қандай HTTP клиент ыңғайлы?",
        "quiz_options": ["requests", "httpx.AsyncClient", "urllib3", "socket"],
        "correct_option_index": 1,
    },
]

LEADERBOARD_DATA = [
    {
        "rank": 1,
        "user_id": "u-001",
        "name": "Айгерім Смағұлова",
        "avatar": "👩‍💻",
        "level": 8,
        "xp": 3420,
        "streak_days": 19,
        "league": "Бриллиант Лига 💎",
    },
    {
        "rank": 2,
        "user_id": "u-002",
        "name": "Дәулет Серікқали",
        "avatar": "👨‍🎓",
        "level": 7,
        "xp": 2890,
        "streak_days": 14,
        "league": "Алтын Лига 🥇",
    },
    {
        "rank": 3,
        "user_id": "u-current",
        "name": "Мансұр Төлеген",
        "avatar": "🚀",
        "level": 5,
        "xp": 1450,
        "streak_days": 7,
        "league": "Алтын Лига 🥇",
        "is_current_user": True,
    },
    {
        "rank": 4,
        "user_id": "u-003",
        "name": "Әсел Қайратқызы",
        "avatar": "👩‍🎓",
        "level": 5,
        "xp": 1380,
        "streak_days": 6,
        "league": "Күміс Лига 🥈",
    },
    {
        "rank": 5,
        "user_id": "u-004",
        "name": "Нұрлан Бақытұлы",
        "avatar": "👨‍💻",
        "level": 4,
        "xp": 1120,
        "streak_days": 4,
        "league": "Күміс Лига 🥈",
    },
    {
        "rank": 6,
        "user_id": "u-005",
        "name": "Мадина Әлім",
        "avatar": "🎨",
        "level": 3,
        "xp": 890,
        "streak_days": 3,
        "league": "Қола Лига 🥉",
    },
]


@router.get("/overview", response_model=GamificationOverview)
async def get_gamification_overview(
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
):
    """
    Студенттің геймификация статистикасы: XP, деңгей, Streak, лигасы және күнделікті квесттер.
    """
    return GamificationOverview(
        user_id=current_user.id,
        level=5,
        current_xp=1450,
        xp_to_next_level=2000,
        level_title="Backend & AI Шебері",
        streak_days=7,
        today_completed=True,
        league="Алтын Лига 🥇",
        weekly_rank=3,
        daily_quests=[
            {"id": "q1", "title": "1 квиз/тест тапсыр", "reward": 50, "current": 1, "target": 1, "completed": True},
            {"id": "q2", "title": "Ollama AI менторға 1 сұрақ қой", "reward": 30, "current": 1, "target": 1, "completed": True},
            {"id": "q3", "title": "Skill Tree бойынша жаңа түйінді аш", "reward": 70, "current": 0, "target": 1, "completed": False},
        ],
    )


@router.get("/skill-tree", response_model=list[SkillNode])
async def get_skill_tree():
    """
    Интерактивті оқу картасындағы барлық түйіндер (Skill Tree nodes).
    """
    return [SkillNode(**node) for node in INITIAL_SKILL_NODES]


class CompleteNodeRequest(BaseModel):
    selected_option_index: int


@router.post("/skill-tree/{node_id}/complete")
async def complete_skill_node(
    node_id: str,
    payload: CompleteNodeRequest,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
):
    """
    Түйін бойынша шағын экспресс-сұраққа жауап беріп, XP ұтып алу және келесі түйінді ашу.
    """
    node = next((n for n in INITIAL_SKILL_NODES if n["id"] == node_id), None)
    if not node:
        raise HTTPException(status_code=404, detail="Түйін табылмады")

    if node["correct_option_index"] != payload.selected_option_index:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Жауап қате! Қайтадан ойланып көріңіз."
        )

    # Дұрыс жауап: түйін аяқталды
    node["status"] = "completed"
    
    # Келесі түйінді ашу (locked -> active)
    curr_index = INITIAL_SKILL_NODES.index(node)
    if curr_index + 1 < len(INITIAL_SKILL_NODES):
        INITIAL_SKILL_NODES[curr_index + 1]["status"] = "active"

    return {
        "success": True,
        "message": f"Керемет! Сіз '{node['title']}' тапсырмасын сәтті орындадыңыз!",
        "xp_earned": node["xp_reward"],
        "new_status": "completed",
    }


@router.get("/leaderboard", response_model=list[LeaderboardEntry])
async def get_leaderboard():
    """
    Үздік студенттер рейтингі (Leaderboard).
    """
    return [LeaderboardEntry(**entry) for entry in LEADERBOARD_DATA]


@router.post("/claim-daily-bonus")
async def claim_daily_bonus(
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
):
    """
    Күнделікті Streak бонусын қабылдау (+50 XP).
    """
    return {
        "success": True,
        "bonus_xp": 50,
        "message": "Күнделікті Streak бонусы есептелді! Жүйелілігіңіз үшін +50 XP берілді 🔥",
    }

