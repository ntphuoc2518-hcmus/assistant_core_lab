"""Persistence with SQLModel (SQLAlchemy + Pydantic) — Lab 5 (R1/R2).

Privacy by design: we store *metadata* about interactions (intent, topic, outcome, latency),
a salted SHA-256 hash of the session id, and feedback. We never store the raw user message,
the raw session id, or any personal student information.

The equivalent SQL lives in ``sql/migrations/001_init.sql``.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, event
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool
from sqlmodel import Field, Session, SQLModel, create_engine, select

VALID_RATINGS = (-1, 0, 1)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ChatSession(SQLModel, table=True):
    __tablename__ = "chat_session"

    id: str = Field(primary_key=True, max_length=16)  # salted hash, never the raw id
    channel: str = Field(default="web", max_length=16)
    created_at: datetime = Field(default_factory=utcnow)


class Interaction(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    request_id: str = Field(index=True, unique=True, max_length=32)
    session_id: str = Field(foreign_key="chat_session.id", index=True)
    intent: str = Field(index=True, max_length=16)
    topic: str | None = Field(default=None, max_length=32)  # e.g. handbook rule id
    resolved: bool = True  # False = the assistant did not know
    degraded: bool = False  # True = a backup answer was used
    latency_ms: float = 0.0
    created_at: datetime = Field(default_factory=utcnow, index=True)


class Feedback(SQLModel, table=True):
    __table_args__ = (CheckConstraint("rating IN (-1, 0, 1)", name="ck_feedback_rating"),)

    id: int | None = Field(default=None, primary_key=True)
    request_id: str = Field(foreign_key="interaction.request_id", index=True, max_length=32)
    rating: int  # -1, 0, 1 — validated at the API, the repository and the database
    comment: str | None = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=utcnow, index=True)


@event.listens_for(Engine, "connect")
def _sqlite_foreign_keys(dbapi_connection, _record) -> None:  # noqa: ANN001
    """SQLite ignores foreign keys unless asked; turn them on for every connection."""
    if dbapi_connection.__class__.__module__.startswith("sqlite3"):
        cur = dbapi_connection.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        cur.close()


def make_engine(url: str) -> Engine:
    """Create an engine. ``sqlite://`` gives a shared in-memory DB (tests); a file URL persists."""
    if url in ("sqlite://", "sqlite:///:memory:"):
        return create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, connect_args=connect_args)


def init_db(engine: Engine) -> None:
    """Create missing tables. Safe to run repeatedly (existing tables are left untouched)."""
    SQLModel.metadata.create_all(engine)


def hash_session(raw: str, salt: str) -> str:
    """One-way, salted SHA-256: same session -> same code, but the code cannot be reversed."""
    return hashlib.sha256((salt + raw).encode("utf-8")).hexdigest()[:16]


class Repository:
    """All database access goes through here — the API never writes SQL."""

    def __init__(self, engine: Engine, salt: str):
        if not salt:
            raise ValueError("a non-empty session salt is required")
        self.engine, self.salt = engine, salt

    def record_interaction(
        self,
        raw_session: str,
        request_id: str,
        intent: str,
        topic: str | None,
        resolved: bool,
        degraded: bool,
        latency_ms: float,
        channel: str = "web",
    ) -> None:
        sid = hash_session(raw_session, self.salt)
        with Session(self.engine) as db:  # one transaction: both rows or neither
            if db.get(ChatSession, sid) is None:
                db.add(ChatSession(id=sid, channel=channel))
            db.add(
                Interaction(
                    request_id=request_id,
                    session_id=sid,
                    intent=intent,
                    topic=topic,
                    resolved=resolved,
                    degraded=degraded,
                    latency_ms=latency_ms,
                )
            )
            db.commit()

    # R1
    def add_feedback(self, request_id: str, rating: int, comment: str | None) -> Feedback | None:
        """Save feedback for a real answer. Returns None when ``request_id`` is unknown (API -> 404)."""
        if rating not in VALID_RATINGS:
            raise ValueError(f"rating must be one of {VALID_RATINGS}")
        with Session(self.engine) as db:
            exists = db.exec(select(Interaction).where(Interaction.request_id == request_id)).first()
            if exists is None:
                return None
            fb = Feedback(request_id=request_id, rating=rating, comment=comment)
            db.add(fb)
            db.commit()
            db.refresh(fb)  # load the id the database just gave it
            return fb

    # R2
    def list_feedback(self, limit: int = 100) -> list[Feedback]:
        """Newest first, at most ``limit`` rows (id breaks ties between equal timestamps)."""
        with Session(self.engine) as db:
            q = select(Feedback).order_by(Feedback.created_at.desc(), Feedback.id.desc()).limit(limit)
            return list(db.exec(q))
