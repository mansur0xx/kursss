from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers.ai import router as ai_router
from app.routers.attempts import router as attempts_router
from app.routers.auth import router as auth_router
from app.routers.health import router as health_router
from app.routers.questions import router as questions_router
from app.routers.quizzes import router as quizzes_router
from app.routers.users import router as users_router

app = FastAPI(
    title=settings.app_name,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    swagger_ui_init_oauth={
        "clientId": settings.KEYCLOAK_CLIENT_ID,
        "usePkceWithAuthorizationCodeGrant": True,
    },
)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(quizzes_router)
app.include_router(questions_router)
app.include_router(attempts_router)
app.include_router(ai_router)
