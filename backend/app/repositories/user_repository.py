from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import Identity
from app.models.user import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> list[User]:
        stmt = select(User).order_by(User.id)
        return list(self.db.scalars(stmt).all())

    def get(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return self.db.scalars(stmt).first()

    def get_by_keycloak_id(self, keycloak_id: str) -> User | None:
        stmt = select(User).where(User.keycloak_id == keycloak_id)
        return self.db.scalars(stmt).first()

    def create(
        self,
        *,
        keycloak_id: str,
        email: str,
        full_name: str,
        role: str = "student",
    ) -> User:
        user = User(
            keycloak_id=keycloak_id,
            email=email,
            full_name=full_name,
            role=role,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def save(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user: User) -> None:
        self.db.delete(user)
        self.db.commit()

    def sync(self, identity: Identity, role: str) -> User:
        user = self.get_by_keycloak_id(identity.keycloak_id)
        if user is None:
            legacy = self.get_by_email(identity.email)
            if legacy and legacy.keycloak_id.startswith("legacy-"):
                user = legacy
                user.keycloak_id = identity.keycloak_id
        if user is None:
            user = User(
                keycloak_id=identity.keycloak_id,
                email=identity.email,
                full_name=identity.full_name,
                role=role,
            )
            self.db.add(user)
        elif (
            (user.email, user.full_name, user.role)
            == (identity.email, identity.full_name, role)
            and not self.db.is_modified(user)
        ):
            return user
        else:
            user.email = identity.email
            user.full_name = identity.full_name
            user.role = role
        self.db.commit()
        self.db.refresh(user)
        return user
