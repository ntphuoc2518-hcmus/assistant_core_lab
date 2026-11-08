"""Lab 5 R1/R2 — Repository tests (SQLite in memory, plus a real file for persistence)."""

import sqlite3

import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from assistant_api.db import ChatSession, Feedback, Interaction, Repository, hash_session, init_db, make_engine

SALT = "test-salt"


def new_repo(url: str = "sqlite://") -> Repository:
    engine = make_engine(url)
    init_db(engine)
    return Repository(engine, SALT)


def record(repo: Repository, request_id: str, session: str = "student-session-1", **kw) -> None:
    args = {"intent": "fee", "topic": None, "resolved": True, "degraded": False, "latency_ms": 1.5}
    args.update(kw)
    repo.record_interaction(raw_session=session, request_id=request_id, **args)


@pytest.fixture
def repo() -> Repository:
    r = new_repo()
    record(r, "req-1")
    return r


# --- session hashing ---------------------------------------------------------------


def test_hash_session_is_stable_salted_and_not_raw():
    h = hash_session("alice-session", SALT)
    assert h == hash_session("alice-session", SALT)  # same input -> same code
    assert h != hash_session("alice-session", "other-salt")  # salt matters
    assert h != hash_session("bob-session", SALT)
    assert len(h) == 16 and all(c in "0123456789abcdef" for c in h)
    assert "alice" not in h


def test_repository_requires_salt():
    with pytest.raises(ValueError):
        Repository(make_engine("sqlite://"), "")


def test_record_interaction_stores_only_hashed_session(repo):
    record(repo, "req-2")  # same session again -> no second chat_session row
    record(repo, "req-3", session="student-session-2")
    with Session(repo.engine) as db:
        sessions = db.exec(select(ChatSession)).all()
        interactions = db.exec(select(Interaction)).all()
    assert {s.id for s in sessions} == {
        hash_session("student-session-1", SALT),
        hash_session("student-session-2", SALT),
    }
    assert len(interactions) == 3
    assert all("student-session" not in i.session_id for i in interactions)


def test_no_raw_message_column():
    cols = set(Interaction.model_fields) | set(ChatSession.model_fields) | set(Feedback.model_fields)
    assert not cols & {"message", "text", "question", "answer", "name", "phone", "email", "student_id"}


# --- R1: add_feedback ----------------------------------------------------------------


def test_add_feedback_valid(repo):
    fb = repo.add_feedback("req-1", 1, "clear answer")
    assert fb is not None and fb.id == 1
    assert (fb.request_id, fb.rating, fb.comment) == ("req-1", 1, "clear answer")
    assert fb.created_at is not None


def test_add_feedback_without_comment(repo):
    fb = repo.add_feedback("req-1", -1, None)
    assert fb is not None and fb.comment is None


def test_add_feedback_unknown_request_id_returns_none_and_saves_nothing(repo):
    assert repo.add_feedback("nope", 1, None) is None
    assert repo.list_feedback() == []


@pytest.mark.parametrize("rating", [-2, 2, 5, 7])
def test_add_feedback_invalid_rating_rejected(repo, rating):
    with pytest.raises(ValueError):
        repo.add_feedback("req-1", rating, None)
    assert repo.list_feedback() == []


def test_database_refuses_invalid_rating(repo):
    """Even bypassing the repository, the CHECK constraint blocks a rating of 7."""
    with Session(repo.engine) as db:
        db.add(Feedback(request_id="req-1", rating=7))
        with pytest.raises(IntegrityError):
            db.commit()


def test_database_refuses_feedback_for_missing_interaction(repo):
    with Session(repo.engine) as db:
        db.add(Feedback(request_id="ghost", rating=1))
        with pytest.raises(IntegrityError):
            db.commit()


def test_request_id_is_unique(repo):
    with pytest.raises(IntegrityError):
        record(repo, "req-1")
    with Session(repo.engine) as db:
        assert len(db.exec(select(Interaction).where(Interaction.request_id == "req-1")).all()) == 1


# --- R2: list_feedback ---------------------------------------------------------------


def test_list_feedback_newest_first_and_limit(repo):
    record(repo, "req-2")
    record(repo, "req-3")
    for rid in ("req-1", "req-2", "req-3"):
        repo.add_feedback(rid, 1, rid)
    listed = repo.list_feedback()
    assert [f.request_id for f in listed] == ["req-3", "req-2", "req-1"]
    assert [f.request_id for f in repo.list_feedback(limit=2)] == ["req-3", "req-2"]


def test_list_feedback_empty():
    assert new_repo().list_feedback() == []


# --- persistence ---------------------------------------------------------------------


def test_feedback_survives_closing_and_reopening_the_database(tmp_path):
    db_file = tmp_path / "assistant.db"
    url = f"sqlite:///{db_file}"

    first = new_repo(url)
    record(first, "req-1")
    first.add_feedback("req-1", -1, "too long")
    first.engine.dispose()  # close every connection, like stopping the server

    second = new_repo(url)  # a brand-new engine on the same file, like restarting
    listed = second.list_feedback()
    assert [(f.request_id, f.rating, f.comment) for f in listed] == [("req-1", -1, "too long")]
    second.engine.dispose()

    # And a plain sqlite3 connection sees the same rows on disk.
    con = sqlite3.connect(db_file)
    try:
        assert con.execute("SELECT request_id, rating FROM feedback").fetchall() == [("req-1", -1)]
    finally:
        con.close()
