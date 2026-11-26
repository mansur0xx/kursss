import json
import time
from pathlib import Path
from uuid import uuid4

from app.core.database import SessionLocal
from app.core.deps import get_token_verifier
from app.core.security import AuthUnavailableError
from app.main import app
from app.models.user import User
from tests.conftest import OTHER_PRIVATE_KEY, bearer, make_token


def test_realm_quizai_json_valid():
    realm_path = Path(__file__).resolve().parents[2] / "keycloak" / "realm-quizai.json"
    assert realm_path.exists()
    data = json.loads(realm_path.read_text(encoding="utf-8"))
    assert data["realm"] == "quizai"
    assert data["registrationAllowed"] is True
    assert data["registrationEmailAsUsername"] is True
    assert data["accessTokenLifespan"] == 300
    assert "student" in data["defaultRole"]["composites"]["realm"]
    web_client = next(c for c in data["clients"] if c["clientId"] == "quizai-web")
    assert web_client["publicClient"] is True
    assert web_client["attributes"]["pkce.code.challenge.method"] == "S256"


def test_missing_and_garbage_token_return_401(client):
    assert client.get("/api/auth/me").status_code == 401
    assert client.get("/api/quizzes").status_code == 401
    assert client.get("/api/auth/me", headers=bearer("not-a-jwt")).status_code == 401


def test_expired_token_returns_401(client):
    past = int(time.time()) - 3600
    token = make_token(str(uuid4()), "e@test.kz", ["student"], iat=past - 300, exp=past)
    assert client.get("/api/auth/me", headers=bearer(token)).status_code == 401


def test_wrong_issuer_audience_and_key_return_401(client):
    wrong_iss = make_token(str(uuid4()), "i@test.kz", ["student"], iss="http://evil.local/realms/x")
    wrong_aud = make_token(str(uuid4()), "a@test.kz", ["student"], aud="other-api")
    wrong_key = make_token(str(uuid4()), "k@test.kz", ["student"], signing_key=OTHER_PRIVATE_KEY)

    assert client.get("/api/auth/me", headers=bearer(wrong_iss)).status_code == 401
    assert client.get("/api/auth/me", headers=bearer(wrong_aud)).status_code == 401
    assert client.get("/api/auth/me", headers=bearer(wrong_key)).status_code == 401


def test_no_app_role_returns_403(client):
    token = make_token(str(uuid4()), "norole@test.kz", [])
    assert client.get("/api/auth/me", headers=bearer(token)).status_code == 403


def test_keycloak_unavailable_returns_503(client):
    class _BrokenVerifier:
        def verify(self, token: str):
            raise AuthUnavailableError("Keycloak down")

    app.dependency_overrides[get_token_verifier] = lambda: _BrokenVerifier()
    token = make_token(str(uuid4()), "s@test.kz", ["student"])
    assert client.get("/api/auth/me", headers=bearer(token)).status_code == 503


def test_first_login_creates_user_and_links_legacy(client):
    # First login creates user
    sub = str(uuid4())
    token = make_token(sub, "new@example.com", ["student"], name="Жаңа Студент")
    res = client.get("/api/auth/me", headers=bearer(token))
    assert res.status_code == 200
    assert res.json()["keycloak_id"] == sub
    assert res.json()["role"] == "student"

    # Legacy user linked by email on first Keycloak login
    with SessionLocal() as db:
        legacy = User(
            keycloak_id="legacy-100",
            email="legacy@example.com",
            full_name="Old Name",
            role="student",
        )
        db.add(legacy)
        db.commit()
        legacy_id = legacy.id

    new_sub = str(uuid4())
    legacy_token = make_token(new_sub, "legacy@example.com", ["teacher"], name="Updated Teacher")
    res2 = client.get("/api/auth/me", headers=bearer(legacy_token))
    assert res2.status_code == 200
    assert res2.json()["id"] == legacy_id
    assert res2.json()["keycloak_id"] == new_sub
    assert res2.json()["role"] == "teacher"


def test_role_matrix_403_for_each_protected_endpoint(client):
    student_h = bearer(make_token(str(uuid4()), "s@example.com", ["student"]))
    teacher1_h = bearer(make_token(str(uuid4()), "t1@example.com", ["teacher"]))
    teacher2_h = bearer(make_token(str(uuid4()), "t2@example.com", ["teacher"]))

    # Student cannot create quiz or access users or results
    assert client.post("/api/quizzes", headers=student_h, json={"title": "Test"}).status_code == 403
    assert client.get("/api/users", headers=student_h).status_code == 403

    # Teacher cannot access /api/users or submit student attempts
    assert client.get("/api/users", headers=teacher1_h).status_code == 403
    assert client.get("/api/attempts/me", headers=teacher1_h).status_code == 403

    # Foreign teacher cannot patch/delete/publish another teacher's quiz
    quiz_id = client.post("/api/quizzes", headers=teacher1_h, json={"title": "T1 Quiz"}).json()["id"]
    assert client.patch(f"/api/quizzes/{quiz_id}", headers=teacher2_h, json={"title": "X"}).status_code == 403
    assert client.delete(f"/api/quizzes/{quiz_id}", headers=teacher2_h).status_code == 403
    assert client.post(f"/api/quizzes/{quiz_id}/publish", headers=teacher2_h).status_code == 403
