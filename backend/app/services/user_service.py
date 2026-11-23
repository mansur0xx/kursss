from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserUpdate
from app.services.exceptions import BadRequestError, ForbiddenError, NotFoundError


class UserService:
    def __init__(self, db: Session) -> None:
        self.repo = UserRepository(db)

    def _ensure_admin(self, current_user: User) -> None:
        if current_user.role != "admin":
            raise ForbiddenError("Тек әкімшіге рұқсат етілген")

    def list_users(self, current_user: User) -> list[User]:
        self._ensure_admin(current_user)
        return self.repo.list()

    def get_user(self, user_id: int, current_user: User) -> User:
        self._ensure_admin(current_user)
        user = self.repo.get(user_id)
        if user is None:
            raise NotFoundError("Пайдаланушы табылмады")
        return user

    def update_user(self, user_id: int, payload: UserUpdate, current_user: User) -> User:
        self._ensure_admin(current_user)
        user = self.repo.get(user_id)
        if user is None:
            raise NotFoundError("Пайдаланушы табылмады")
        if user.id == current_user.id and payload.role is not None:
            raise BadRequestError("Өз рөліңізді өзгертуге болмайды")
        if payload.full_name is not None:
            user.full_name = payload.full_name
        if payload.role is not None:
            user.role = payload.role
        return self.repo.save(user)

    def delete_user(self, user_id: int, current_user: User) -> None:
        self._ensure_admin(current_user)
        user = self.repo.get(user_id)
        if user is None:
            raise NotFoundError("Пайдаланушы табылмады")
        if user.id == current_user.id:
            raise BadRequestError("Өзіңізді өшіруге болмайды")
        self.repo.delete(user)
