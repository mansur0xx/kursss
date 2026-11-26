from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

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

    def sync(self, identity: dict[str, Any], role: str) -> User:
        sub = str(identity["sub"])
        email = str(
            identity.get("email")
            or identity.get("preferred_username")
            or f"{sub}@quizai.local"
        )
        full_name = str(
            identity.get("name")
            or f"{identity.get('given_name', '')} {identity.get('family_name', '')}".strip()
            or email.split("@")[0]
        )[:120]

        user = self.get_by_keycloak_id(sub)
        if user is None:
            user = self.get_by_email(email)
            if user is not None:
                user.keycloak_id = sub
                user.full_name = full_name
                user.role = role
                return self.save(user)
            return self.create(
                keycloak_id=sub,
                email=email,
                full_name=full_name,
                role=role,
            )

        changed = False
        if user.email != email:
            user.email = email
            changed = True
        if user.full_name != full_name:
            user.full_name = full_name
            changed = True
        if user.role != role:
            user.role = role
            changed = True
        return self.save(user) if changed else user
