from fastapi.testclient import TestClient

from app.core.database import SessionLocal
from app.main import app
from app.models.user import User

client = TestClient(app)


def _create_admin() -> int:
    with SessionLocal() as db:
        admin = User(email="admin@example.com", full_name="Admin User", role="admin")
        db.add(admin)
        db.commit()
        db.refresh(admin)
        return admin.id


def test_module_1_2_auth_register_and_login():
    # Register valid student
    r = client.post(
        "/api/auth/register",
        json={
            "email": "s1@example.com",
            "full_name": "Student One",
            "password": "password123",
            "role": "student",
        },
    )
    assert r.status_code == 201
    data = r.json()
    assert data["email"] == "s1@example.com"
    assert "password" not in data

    # Duplicate email -> 409
    r_dup = client.post(
        "/api/auth/register",
        json={
            "email": "s1@example.com",
            "full_name": "Student One",
            "password": "password123",
            "role": "student",
        },
    )
    assert r_dup.status_code == 409

    # Short password -> 422
    r_short = client.post(
        "/api/auth/register",
        json={
            "email": "s2@example.com",
            "full_name": "Student Two",
            "password": "123",
            "role": "student",
        },
    )
    assert r_short.status_code == 422

    # role: admin in body -> 422
    r_admin = client.post(
        "/api/auth/register",
        json={
            "email": "a@example.com",
            "full_name": "Fake Admin",
            "password": "password123",
            "role": "admin",
        },
    )
    assert r_admin.status_code == 422

    # Login valid -> 200
    r_login = client.post(
        "/api/auth/login",
        json={"email": "s1@example.com", "password": "password123"},
    )
    assert r_login.status_code == 200

    # Login invalid -> 401 «Email немесе құпиясөз қате»
    r_bad = client.post(
        "/api/auth/login",
        json={"email": "s1@example.com", "password": "wrongpassword"},
    )
    assert r_bad.status_code == 401
    assert r_bad.json()["detail"] == "Email немесе құпиясөз қате"


def test_module_3_users_admin_only():
    admin_id = _create_admin()
    t_res = client.post(
        "/api/auth/register",
        json={
            "email": "t1@example.com",
            "full_name": "Teacher One",
            "password": "password123",
            "role": "teacher",
        },
    )
    teacher_id = t_res.json()["id"]

    # Teacher -> 403
    assert client.get("/api/users", headers={"X-User-Id": str(teacher_id)}).status_code == 403

    # Admin -> 200
    res_list = client.get("/api/users", headers={"X-User-Id": str(admin_id)})
    assert res_list.status_code == 200
    assert len(res_list.json()) == 2

    # GET /api/users/{id} -> 200 and 404
    assert (
        client.get(f"/api/users/{teacher_id}", headers={"X-User-Id": str(admin_id)}).status_code
        == 200
    )
    assert client.get("/api/users/9999", headers={"X-User-Id": str(admin_id)}).status_code == 404

    # PATCH /api/users/{id} -> 200, changing own role -> 400
    r_patch = client.patch(
        f"/api/users/{teacher_id}",
        headers={"X-User-Id": str(admin_id)},
        json={"full_name": "Updated Teacher", "role": "student"},
    )
    assert r_patch.status_code == 200
    assert r_patch.json()["full_name"] == "Updated Teacher"
    assert r_patch.json()["role"] == "student"

    r_self_role = client.patch(
        f"/api/users/{admin_id}",
        headers={"X-User-Id": str(admin_id)},
        json={"role": "teacher"},
    )
    assert r_self_role.status_code == 400

    # DELETE /api/users/{id} -> self 400, other 204
    assert (
        client.delete(f"/api/users/{admin_id}", headers={"X-User-Id": str(admin_id)}).status_code
        == 400
    )
    assert (
        client.delete(
            f"/api/users/{teacher_id}", headers={"X-User-Id": str(admin_id)}
        ).status_code
        == 204
    )


def test_modules_4_5_6_quizzes_questions_publish_and_attempts():
    t1 = client.post(
        "/api/auth/register",
        json={
            "email": "t1@example.com",
            "full_name": "T1",
            "password": "password123",
            "role": "teacher",
        },
    ).json()["id"]
    t2 = client.post(
        "/api/auth/register",
        json={
            "email": "t2@example.com",
            "full_name": "T2",
            "password": "password123",
            "role": "teacher",
        },
    ).json()["id"]
    s1 = client.post(
        "/api/auth/register",
        json={
            "email": "s1@example.com",
            "full_name": "S1",
            "password": "password123",
            "role": "student",
        },
    ).json()["id"]

    # Create quiz by T1 -> 201
    q_res = client.post(
        "/api/quizzes",
        headers={"X-User-Id": str(t1)},
        json={"title": "Python Basics", "topic": "Python"},
    )
    assert q_res.status_code == 201
    quiz_id = q_res.json()["id"]

    # Publish without questions -> 400
    assert (
        client.post(
            f"/api/quizzes/{quiz_id}/publish", headers={"X-User-Id": str(t1)}
        ).status_code
        == 400
    )

    # Foreign teacher T2 cannot patch or delete -> 403
    assert (
        client.patch(
            f"/api/quizzes/{quiz_id}",
            headers={"X-User-Id": str(t2)},
            json={"title": "Hacked"},
        ).status_code
        == 403
    )
    assert (
        client.delete(f"/api/quizzes/{quiz_id}", headers={"X-User-Id": str(t2)}).status_code
        == 403
    )

    # Add question with invalid correct_index -> 400
    assert (
        client.post(
            f"/api/quizzes/{quiz_id}/questions",
            headers={"X-User-Id": str(t1)},
            json={"prompt": "2+2?", "options": ["3", "4"], "correct_index": 5},
        ).status_code
        == 400
    )

    # Add valid question -> 201
    question_res = client.post(
        f"/api/quizzes/{quiz_id}/questions",
        headers={"X-User-Id": str(t1)},
        json={"prompt": "2+2?", "options": ["3", "4"], "correct_index": 1},
    )
    assert question_res.status_code == 201
    question_id = question_res.json()["id"]

    # Patch question by T1 -> 200, by T2 -> 403
    assert (
        client.patch(
            f"/api/questions/{question_id}",
            headers={"X-User-Id": str(t2)},
            json={"prompt": "Bad"},
        ).status_code
        == 403
    )
    assert (
        client.patch(
            f"/api/questions/{question_id}",
            headers={"X-User-Id": str(t1)},
            json={"prompt": "What is 2 + 2?"},
        ).status_code
        == 200
    )

    # Publish quiz -> 200
    pub_res = client.post(f"/api/quizzes/{quiz_id}/publish", headers={"X-User-Id": str(t1)})
    assert pub_res.status_code == 200
    assert pub_res.json()["is_published"] is True

    # Cannot add/patch/delete question in published quiz -> 400
    assert (
        client.post(
            f"/api/quizzes/{quiz_id}/questions",
            headers={"X-User-Id": str(t1)},
            json={"prompt": "New?", "options": ["A", "B"], "correct_index": 0},
        ).status_code
        == 400
    )
    assert (
        client.patch(
            f"/api/questions/{question_id}",
            headers={"X-User-Id": str(t1)},
            json={"prompt": "Change"},
        ).status_code
        == 400
    )
    assert (
        client.delete(
            f"/api/questions/{question_id}",
            headers={"X-User-Id": str(t1)},
        ).status_code
        == 400
    )

    # Student gets quiz WITHOUT correct_index
    s_quiz = client.get(f"/api/quizzes/{quiz_id}", headers={"X-User-Id": str(s1)})
    assert s_quiz.status_code == 200
    assert "correct_index" not in s_quiz.json()["questions"][0]

    # Submit attempt with wrong answer count -> 400
    assert (
        client.post(
            f"/api/quizzes/{quiz_id}/attempts",
            headers={"X-User-Id": str(s1)},
            json={"answers": [0, 1]},
        ).status_code
        == 400
    )

    # Submit valid attempt -> 201
    att_res = client.post(
        f"/api/quizzes/{quiz_id}/attempts",
        headers={"X-User-Id": str(s1)},
        json={"answers": [1]},
    )
    assert att_res.status_code == 201
    assert att_res.json()["score"] == 1
    assert att_res.json()["total"] == 1

    # GET /api/attempts/me -> 200
    me_res = client.get("/api/attempts/me", headers={"X-User-Id": str(s1)})
    assert me_res.status_code == 200
    assert len(me_res.json()) == 1
