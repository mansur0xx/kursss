import hashlib
import hmac

from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserLogin, UserRegister
from app.services.exceptions import ConflictError, UnauthorizedError

_PASSWORD_HASHES: dict[str, str] = {}
_LAST_USER_ID: int | None = None


def _hash_password(email: str, password: str) -> str:
    salt = email.lower().encode("utf-8")
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000).hex()


def get_last_authenticated_user_id() -> int | None:
    return _LAST_USER_ID


def set_last_authenticated_user_id(user_id: int | None) -> None:
    global _LAST_USER_ID
    _LAST_USER_ID = user_id


def reset_auth_state() -> None:
    global _LAST_USER_ID
    _PASSWORD_HASHES.clear()
    _LAST_USER_ID = None


class AuthService:
    def __init__(self, db: Session) -> None:
        self.repo = UserRepository(db)

    def register(self, payload: UserRegister) -> User:
        existing = self.repo.get_by_email(payload.email)
        if existing is not None:
            raise ConflictError("Бұл email тіркелген")
        user = self.repo.create(
            email=payload.email,
            full_name=payload.full_name,
            role=payload.role,
        )
        _PASSWORD_HASHES[payload.email] = _hash_password(payload.email, payload.password)
        set_last_authenticated_user_id(user.id)
        return user

    def login(self, payload: UserLogin) -> User:
        user = self.repo.get_by_email(payload.email)
        if user is None:
            raise UnauthorizedError("Email немесе құпиясөз қате")
        stored_hash = _PASSWORD_HASHES.get(payload.email)
        candidate_hash = _hash_password(payload.email, payload.password)
        if stored_hash is None or not hmac.compare_digest(stored_hash, candidate_hash):
            raise UnauthorizedError("Email немесе құпиясөз қате")
        set_last_authenticated_user_id(user.id)
        return user
