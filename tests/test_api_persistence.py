"""Lab 5 — the real API uses the Repository (not an in-memory list)."""

import sqlite3

import httpx
import pytest
from fastapi.testclient import TestClient

from assistant_api.db import hash_session
from assistant_api.main import create_app
from assistant_api.weather import WeatherClient
from assistant_core.errors import ConfigError

ADMIN = {"X-API-Key": "secret-admin"}


def no_weather() -> WeatherClient:
    return WeatherClient("https://example.test", 0, 0, transport=httpx.MockTransport(lambda r: httpx.Response(500)))


def make_client(settings, service, **update) -> TestClient:
    settings = settings.model_copy(update={"api_admin_key": "secret-admin", **update})
    return TestClient(create_app(settings, service, no_weather()))


@pytest.fixture
def client(settings, service):
    return make_client(settings, service)


def ask(client: TestClient, message: str = "tuition for 18 credits and 2 retake", session: str = "s1") -> str:
    r = client.post("/v1/chat", json={"message": message, "session_id": session})
    assert r.status_code == 200
    return r.json()["request_id"]


def test_valid_feedback_is_saved(client):
    rid = ask(client)
    r = client.post("/v1/feedback", json={"request_id": rid, "rating": 1, "comment": "clear"})
    assert r.status_code == 201
    body = r.json()
    assert body["request_id"] == rid and body["rating"] == 1 and body["comment"] == "clear"
    assert body["id"] == 1 and body["created_at"]


def test_feedback_unknown_request_id_is_404(client):
    r = client.post("/v1/feedback", json={"request_id": "nope", "rating": 1})
    assert r.status_code == 404
    assert r.json() == {"error": {"code": "request_not_found", "message": "Request not found"}}
    assert client.get("/v1/feedback", headers=ADMIN).json() == []


@pytest.mark.parametrize("rating", [-2, 2, 7, "good"])
def test_feedback_invalid_rating_is_422(client, rating):
    rid = ask(client)
    r = client.post("/v1/feedback", json={"request_id": rid, "rating": rating})
    assert r.status_code == 422 and r.json()["error"]["code"] == "invalid_request"


def test_list_feedback_newest_first_admin_only(client):
    ids = [ask(client, "hello") for _ in range(3)]
    for i, rid in enumerate(ids):
        assert client.post("/v1/feedback", json={"request_id": rid, "rating": 1, "comment": str(i)}).status_code == 201
    assert client.get("/v1/feedback").status_code == 401
    assert client.get("/v1/feedback", headers={"X-API-Key": "wrong"}).status_code == 401
    listed = client.get("/v1/feedback", headers=ADMIN).json()
    assert [f["request_id"] for f in listed] == list(reversed(ids))
    limited = client.get("/v1/feedback", params={"limit": 2}, headers=ADMIN).json()
    assert [f["request_id"] for f in limited] == list(reversed(ids))[:2]


def test_chat_stores_metadata_but_not_message_or_raw_session(settings, service, tmp_path):
    db_file = tmp_path / "assistant.db"
    client = make_client(settings, service, database_url=f"sqlite:///{db_file}")
    secret_text = "my name is Nguyen Van A, phone 0901234567, can I register my thesis with 118 credits"
    rid = ask(client, secret_text, session="raw-session-xyz")

    con = sqlite3.connect(db_file)
    try:
        dump = "\n".join(con.iterdump())
        row = con.execute(
            "SELECT session_id, intent, resolved FROM interaction WHERE request_id = ?", (rid,)
        ).fetchone()
    finally:
        con.close()
    assert row == (hash_session("raw-session-xyz", settings.session_salt), "rule", 1)
    for leaked in ("Nguyen", "0901234567", "thesis", "raw-session-xyz"):
        assert leaked not in dump


def test_feedback_survives_app_restart(settings, service, tmp_path):
    url = f"sqlite:///{tmp_path / 'assistant.db'}"
    first = make_client(settings, service, database_url=url)
    rid = ask(first)
    assert first.post("/v1/feedback", json={"request_id": rid, "rating": -1}).status_code == 201
    del first

    second = make_client(settings, service, database_url=url)  # brand-new app, same file
    listed = second.get("/v1/feedback", headers=ADMIN).json()
    assert [(f["request_id"], f["rating"]) for f in listed] == [(rid, -1)]
    # the old request_id is still known after the restart
    assert second.post("/v1/feedback", json={"request_id": rid, "rating": 1}).status_code == 201


def test_api_requires_session_salt(settings, service):
    with pytest.raises(ConfigError):
        create_app(settings.model_copy(update={"session_salt": ""}), service, no_weather())
