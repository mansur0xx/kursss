import base64
import json
import time

from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.database import SessionLocal
from app.main import app
from app.models.user import User

client = TestClient(app)


def _kc_headers(sub: str, email: str, name: str, role: str) -> dict[str, str]:
    now = int(time.time())
    header = {"alg": "RS256", "typ": "JWT"}
    payload = {
        "sub": sub,
        "iss": settings.keycloak_issuer,
        "aud": settings.KEYCLOAK_AUDIENCE,
        "exp": now + 300,
        "email": email,
        "name": name,
        "realm_access": {"roles": [role]},
    }
    h = base64.urlsafe_b64encode(json.dumps(header).encode()).rstrip(b"=").decode()
    p = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b"=").decode()
    s = base64.urlsafe_b64encode(b"sig").rstrip(b"=").decode()
    return {"Authorization": f"Bearer {h}.{p}.{s}"}


def test_auth_me_and_removed_legacy_endpoints():
    # Old register and login endpoints are removed (404)
    assert client.post("/api/auth/register", json={}).status_code == 404
    assert client.post("/api/auth/login", json={}).status_code == 404

    # Without token -> 401
    assert client.get("/api/auth/me").status_code == 401

    # With Keycloak token -> 200 and synced to DB
    headers = _kc_headers("kc-s1", "s1@example.com", "Student One", "student")
    res = client.get("/api/auth/me", headers=headers)
    assert res.status_code == 200
    body = res.json()
    assert body["keycloak_id"] == "kc-s1"
    assert body["email"] == "s1@example.com"
    assert body["role"] == "student"


def test_users_admin_only_without_patch():
    admin_h = _kc_headers("kc-admin", "admin@example.com", "Admin User", "admin")
    teacher_h = _kc_headers("kc-t1", "t1@example.com", "Teacher One", "teacher")

    admin_id = client.get("/api/auth/me", headers=admin_h).json()["id"]
    teacher_id = client.get("/api/auth/me", headers=teacher_h).json()["id"]

    # Teacher -> 403
    assert client.get("/api/users", headers=teacher_h).status_code == 403

    # Admin -> 200 list
    res_list = client.get("/api/users", headers=admin_h)
    assert res_list.status_code == 200
    assert len(res_list.json()) == 2

    # GET /api/users/{id} -> 200 and 404
    assert client.get(f"/api/users/{teacher_id}", headers=admin_h).status_code == 200
    assert client.get("/api/users/9999", headers=admin_h).status_code == 404

    # PATCH /api/users/{id} is removed (405 Method Not Allowed)
    assert client.patch(f"/api/users/{teacher_id}", headers=admin_h, json={}).status_code == 405

    # DELETE /api/users/{id} -> self 400, other 204
    assert client.delete(f"/api/users/{admin_id}", headers=admin_h).status_code == 400
    assert client.delete(f"/api/users/{teacher_id}", headers=admin_h).status_code == 204


def test_quizzes_questions_ai_publish_attempts_and_csv():
    t1_h = _kc_headers("kc-t1", "t1@example.com", "T1", "teacher")
    t2_h = _kc_headers("kc-t2", "t2@example.com", "T2", "teacher")
    s1_h = _kc_headers("kc-s1", "s1@example.com", "S1", "student")

    # Create quiz by T1 -> 201
    q_res = client.post(
        "/api/quizzes",
        headers=t1_h,
        json={"title": "Python Basics", "topic": "Python"},
    )
    assert q_res.status_code == 201
    quiz_id = q_res.json()["id"]

    # Publish without questions -> 400
    assert client.post(f"/api/quizzes/{quiz_id}/publish", headers=t1_h).status_code == 400

    # Foreign teacher T2 cannot patch or delete -> 403
    assert (
        client.patch(f"/api/quizzes/{quiz_id}", headers=t2_h, json={"title": "Hacked"}).status_code
        == 403
    )
    assert client.delete(f"/api/quizzes/{quiz_id}", headers=t2_h).status_code == 403

    # AI generation (fallback when Ollama is offline) -> 201
    gen_res = client.post(
        f"/api/quizzes/{quiz_id}/generate-questions",
        headers=t1_h,
        json={"topic": "Python", "count": 2},
    )
    assert gen_res.status_code == 201
    assert len(gen_res.json()["questions"]) == 2

    # Add invalid correct_index -> 400
    assert (
        client.post(
            f"/api/quizzes/{quiz_id}/questions",
            headers=t1_h,
            json={"prompt": "2+2?", "options": ["3", "4"], "correct_index": 5},
        ).status_code
        == 400
    )

    # Publish quiz -> 200
    pub_res = client.post(f"/api/quizzes/{quiz_id}/publish", headers=t1_h)
    assert pub_res.status_code == 200
    assert pub_res.json()["is_published"] is True

    # Student gets quiz WITHOUT correct_index
    s_quiz = client.get(f"/api/quizzes/{quiz_id}", headers=s1_h)
    assert s_quiz.status_code == 200
    assert "correct_index" not in s_quiz.json()["questions"][0]

    # Submit wrong count -> 400
    assert (
        client.post(f"/api/quizzes/{quiz_id}/attempts", headers=s1_h, json={"answers": [0]}).status_code
        == 400
    )

    # Submit valid attempt -> 201
    att_res = client.post(
        f"/api/quizzes/{quiz_id}/attempts",
        headers=s1_h,
        json={"answers": [0, 1]},
    )
    assert att_res.status_code == 201
    assert att_res.json()["score"] == 2
    assert att_res.json()["total"] == 2

    # GET /api/attempts/me -> 200
    assert len(client.get("/api/attempts/me", headers=s1_h).json()) == 1

    # Teacher results & CSV export
    res_summary = client.get(f"/api/quizzes/{quiz_id}/results", headers=t1_h)
    assert res_summary.status_code == 200
    assert res_summary.json()["average_percent"] == 100.0

    csv_res = client.get(f"/api/quizzes/{quiz_id}/results/export", headers=t1_h)
    assert csv_res.status_code == 200
    assert "text/csv" in csv_res.headers["content-type"]


def test_sync_links_legacy_user_by_email_and_updates_changes():
    with SessionLocal() as db:
        legacy = User(
            keycloak_id="legacy-temp-id",
            email="legacy@demo.kz",
            full_name="Old Name",
            role="student",
        )
        db.add(legacy)
        db.commit()
        legacy_id = legacy.id

    headers = _kc_headers("kc-new-uuid-999", "legacy@demo.kz", "New Name", "teacher")
    res = client.get("/api/auth/me", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == legacy_id
    assert data["keycloak_id"] == "kc-new-uuid-999"
    assert data["full_name"] == "New Name"
    assert data["role"] == "teacher"
