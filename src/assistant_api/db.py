from datetime import datetime, timezone

from sqlalchemy.engine import Engine
from sqlmodel import Field, Session, SQLModel, create_engine, select


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ChatSession(SQLModel, table=True):
    __tablename__ = "chat_session"

    id: str = Field(primary_key=True)


class Interaction(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    request_id: str = Field(index=True, unique=True)
    session_id: str = Field(foreign_key="chat_session.id")
    intent: str
    topic: str | None = None
    resolved: bool = True
    degraded: bool = False
    latency_ms: float = 0.0
    created_at: datetime = Field(default_factory=utcnow)


class Feedback(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    request_id: str = Field(foreign_key="interaction.request_id", index=True)
    rating: int = Field(ge=-1, le=1)
    comment: str | None = None
    created_at: datetime = Field(default_factory=utcnow)


class Repository:
    def __init__(self, database_url: str = "sqlite:///assistant.db") -> None:
        connect_args = (
            {"check_same_thread": False}
            if database_url.startswith("sqlite")
            else {}
        )

        self.engine: Engine = create_engine(
            database_url,
            connect_args=connect_args,
        )

        SQLModel.metadata.create_all(self.engine)

    def add_feedback(
        self,
        request_id: str,
        rating: int,
        comment: str | None,
    ) -> Feedback | None:
        with Session(self.engine) as db:
            exists = db.exec(
                select(Interaction).where(
                    Interaction.request_id == request_id
                )
            ).first()

            if exists is None:
                return None

            fb = Feedback(
                request_id=request_id,
                rating=rating,
                comment=comment,
            )

            db.add(fb)
            db.commit()
            db.refresh(fb)

            return fb
