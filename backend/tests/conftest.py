import time
from typing import Any

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient

from app.core.config import settings

# Тесттер кестелерді өшіріп-қайта жасайды → тек
# бөлек тест-дерекқорда: quizai → quizai_test
if not settings.database_url.endswith("_test"):
    settings.database_url += "_test"

import app.models  # noqa: E402,F401
from app.core.database import Base, engine  # noqa: E402
from app.core.deps import get_token_verifier  # noqa: E402
from app.main import app  # noqa: E402

_PRIVATE_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
_PUBLIC_KEY = _PRIVATE_KEY.public_key()
OTHER_PRIVATE_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)


class _TestRSAVerifier:
    def __init__(self, public_key: Any, issuer: str, audience: str) -> None:
        self.public_key = public_key
        self.issuer = issuer
        self.audience = audience

    def verify(self, token: str) -> dict[str, Any]:
        return jwt.decode(
            token,
            self.public_key,
            algorithms=["RS256"],
            issuer=self.issuer,
            audience=self.audience,
            options={"require": ["exp", "iat", "iss", "sub", "aud"]},
        )


def make_token(
    sub: str,
    email: str,
    roles: list[str],
    *,
    name: str | None = None,
    signing_key: Any = None,
    **overrides: Any,
) -> str:
    now = int(time.time())
    claims: dict[str, Any] = {
        "sub": sub,
        "iss": settings.keycloak_issuer,
        "aud": settings.keycloak_audience,
        "iat": now,
        "exp": now + 300,
        "email": email,
        "name": name or email.split("@")[0],
        "realm_access": {"roles": roles},
    }
    claims.update(overrides)
    return jwt.encode(claims, signing_key or _PRIVATE_KEY, algorithm="RS256")


def bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(autouse=True)
def clean_state():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    app.dependency_overrides[get_token_verifier] = lambda: _TestRSAVerifier(
        _PUBLIC_KEY,
        settings.keycloak_issuer,
        settings.keycloak_audience,
    )
    yield
    app.dependency_overrides.clear()


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)
