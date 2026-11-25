import base64
import json
import time
from pathlib import Path

from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app

client = TestClient(app)


def _make_fake_kc_token(payload: dict) -> str:
    header = {"alg": "RS256", "typ": "JWT"}
    h = base64.urlsafe_b64encode(json.dumps(header).encode()).rstrip(b"=").decode()
    p = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b"=").decode()
    s = base64.urlsafe_b64encode(b"sig").rstrip(b"=").decode()
    return f"{h}.{p}.{s}"


def test_realm_quizai_json_matches_lesson_10_requirements():
    realm_path = Path(__file__).resolve().parents[2] / "keycloak" / "realm-quizai.json"
    assert realm_path.exists()
    data = json.loads(realm_path.read_text(encoding="utf-8"))

    assert data["realm"] == "quizai"
    assert data["registrationAllowed"] is True
    assert data["registrationEmailAsUsername"] is True
    assert data["accessTokenLifespan"] == 300

    role_names = {r["name"] for r in data["roles"]["realm"]}
    assert {"student", "teacher", "admin"}.issubset(role_names)
    assert "student" in data["defaultRole"]["composites"]["realm"]

    web_client = next(c for c in data["clients"] if c["clientId"] == "quizai-web")
    assert web_client["publicClient"] is True
    assert web_client["attributes"]["pkce.code.challenge.method"] == "S256"

    aud_mapper = next(
        m for m in web_client["protocolMappers"] if m["protocolMapper"] == "oidc-audience-mapper"
    )
    assert aud_mapper["config"]["included.custom.audience"] == "quizai-api"
    assert aud_mapper["config"]["access.token.claim"] == "true"

    demo_emails = {u["email"] for u in data["users"]}
    assert {"teacher@demo.kz", "student@demo.kz", "admin@demo.kz"}.issubset(demo_emails)


def test_keycloak_oidc_token_syncs_user_and_checks_audience():
    now = int(time.time())
    valid_token = _make_fake_kc_token(
        {
            "sub": "kc-uuid-teacher-001",
            "iss": settings.keycloak_issuer,
            "aud": settings.KEYCLOAK_AUDIENCE,
            "exp": now + 300,
            "email": "teacher@demo.kz",
            "name": "Demo Teacher",
            "realm_access": {"roles": ["teacher"]},
        }
    )

    # Create quiz using Keycloak OIDC token -> auto-provisions teacher in PostgreSQL
    res = client.post(
        "/api/quizzes",
        headers={"Authorization": f"Bearer {valid_token}"},
        json={"title": "Keycloak OIDC Quiz", "topic": "Security"},
    )
    assert res.status_code == 201
    assert res.json()["title"] == "Keycloak OIDC Quiz"

    # Token with wrong audience -> 401
    wrong_aud_token = _make_fake_kc_token(
        {
            "sub": "kc-uuid-student-002",
            "iss": settings.keycloak_issuer,
            "aud": "other-api",
            "exp": now + 300,
            "email": "student@demo.kz",
            "realm_access": {"roles": ["student"]},
        }
    )
    res_bad = client.get(
        "/api/quizzes",
        headers={"Authorization": f"Bearer {wrong_aud_token}"},
    )
    assert res_bad.status_code == 401
