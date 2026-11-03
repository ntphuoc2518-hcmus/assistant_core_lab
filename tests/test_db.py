
from sqlmodel import Session, select

from assistant_api.db import ChatSession, Feedback, Interaction, Repository


def create_repository() -> Repository:
    repo = Repository("sqlite://")

    with Session(repo.engine) as db:
        db.add(ChatSession(id="session-1"))
        db.add(
            Interaction(
                request_id="request-123",
                session_id="session-1",
                intent="fee",
            )
        )
        db.commit()

    return repo


def test_add_feedback_success():
    repo = create_repository()

    feedback = repo.add_feedback(
        request_id="request-123",
        rating=1,
        comment="Helpful answer",
    )

    assert feedback is not None
    assert feedback.id == 1
    assert feedback.request_id == "request-123"
    assert feedback.rating == 1
    assert feedback.comment == "Helpful answer"


def test_add_feedback_without_comment():
    repo = create_repository()

    feedback = repo.add_feedback(
        request_id="request-123",
        rating=-1,
        comment=None,
    )

    assert feedback is not None
    assert feedback.comment is None


def test_add_feedback_invalid_request_id():
    repo = create_repository()

    feedback = repo.add_feedback(
        request_id="invalid-id",
        rating=-1,
        comment=None,
    )

    assert feedback is None

    with Session(repo.engine) as db:
        saved_feedback = db.exec(select(Feedback)).all()

    assert len(saved_feedback) == 0
