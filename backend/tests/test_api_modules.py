from uuid import uuid4

from tests.conftest import bearer, make_token


def test_removed_legacy_auth_endpoints(client):
    assert client.post("/api/auth/register", json={}).status_code == 404
    assert client.post("/api/auth/login", json={}).status_code == 404


def test_users_admin_only_without_patch(client):
    admin_h = bearer(make_token(str(uuid4()), "admin@example.com", ["admin"], name="Admin User"))
    teacher_h = bearer(make_token(str(uuid4()), "t1@example.com", ["teacher"], name="Teacher One"))

    admin_id = client.get("/api/auth/me", headers=admin_h).json()["id"]
    teacher_id = client.get("/api/auth/me", headers=teacher_h).json()["id"]

    assert client.get("/api/users", headers=teacher_h).status_code == 403
    res_list = client.get("/api/users", headers=admin_h)
    assert res_list.status_code == 200
    assert len(res_list.json()) == 2

    assert client.get(f"/api/users/{teacher_id}", headers=admin_h).status_code == 200
    assert client.get("/api/users/9999", headers=admin_h).status_code == 404
    assert client.patch(f"/api/users/{teacher_id}", headers=admin_h, json={}).status_code == 405
    assert client.delete(f"/api/users/{admin_id}", headers=admin_h).status_code == 400
    assert client.delete(f"/api/users/{teacher_id}", headers=admin_h).status_code == 204


def test_quizzes_questions_ai_publish_attempts_and_csv(client):
    t1_h = bearer(make_token(str(uuid4()), "t1@example.com", ["teacher"], name="T1"))
    t2_h = bearer(make_token(str(uuid4()), "t2@example.com", ["teacher"], name="T2"))
    s1_h = bearer(make_token(str(uuid4()), "s1@example.com", ["student"], name="S1"))

    q_res = client.post(
        "/api/quizzes",
        headers=t1_h,
        json={"title": "Python Basics", "topic": "Python"},
    )
    assert q_res.status_code == 201
    quiz_id = q_res.json()["id"]

    # Publish without questions -> 400
    assert client.post(f"/api/quizzes/{quiz_id}/publish", headers=t1_h).status_code == 400

    # Foreign teacher T2 -> 403
    assert client.patch(f"/api/quizzes/{quiz_id}", headers=t2_h, json={"title": "Hacked"}).status_code == 403
    assert client.delete(f"/api/quizzes/{quiz_id}", headers=t2_h).status_code == 403

    # AI generation (fallback when Ollama is offline) -> 201
    gen_res = client.post(
        f"/api/quizzes/{quiz_id}/generate-questions",
        headers=t1_h,
        json={"topic": "Python", "count": 2},
    )
    assert gen_res.status_code == 201
    assert len(gen_res.json()["questions"]) == 2

    # Invalid correct_index -> 400
    assert (
        client.post(
            f"/api/quizzes/{quiz_id}/questions",
            headers=t1_h,
            json={"prompt": "2+2?", "options": ["3", "4"], "correct_index": 5},
        ).status_code
        == 400
    )

    # Publish -> 200
    pub_res = client.post(f"/api/quizzes/{quiz_id}/publish", headers=t1_h)
    assert pub_res.status_code == 200
    assert pub_res.json()["is_published"] is True

    # Student gets quiz WITHOUT correct_index
    s_quiz = client.get(f"/api/quizzes/{quiz_id}", headers=s1_h)
    assert s_quiz.status_code == 200
    assert "correct_index" not in s_quiz.json()["questions"][0]

    # Wrong answer count -> 400
    assert (
        client.post(f"/api/quizzes/{quiz_id}/attempts", headers=s1_h, json={"answers": [0]}).status_code
        == 400
    )

    # Valid attempt -> 201
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
