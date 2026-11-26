from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.routers.ai import router as ai_router
from app.routers.attempts import router as attempts_router
from app.routers.auth import router as auth_router
from app.routers.health import router as health_router
from app.routers.questions import router as questions_router
from app.routers.quizzes import router as quizzes_router
from app.routers.users import router as users_router
from app.services import errors
from app.services import exceptions as legacy_errors

app = FastAPI(
    title=settings.app_name,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    swagger_ui_init_oauth={
        "clientId": settings.keycloak_client_id,
        "usePkceWithAuthorizationCodeGrant": True,
        "scopes": "openid",
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

_ERROR_CODES = {
    errors.NotFoundError: 404,
    errors.ForbiddenError: 403,
    errors.ConflictError: 409,
    errors.AuthError: 401,
    errors.BadRequestError: 400,
    legacy_errors.NotFoundError: 404,
    legacy_errors.ForbiddenError: 403,
    legacy_errors.ConflictError: 409,
    legacy_errors.UnauthorizedError: 401,
    legacy_errors.BadRequestError: 400,
}


def _handler(code: int):
    async def handle(_: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(status_code=code, content={"detail": str(exc)})

    return handle


for _exc_class, _code in _ERROR_CODES.items():
    app.add_exception_handler(_exc_class, _handler(_code))

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(quizzes_router)
app.include_router(questions_router)
app.include_router(attempts_router)
app.include_router(ai_router)
