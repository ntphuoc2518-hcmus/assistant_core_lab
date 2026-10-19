from pathlib import Path

import pytest

from assistant_core.config import Settings
from assistant_core.knowledge import Handbook, OfficeDirectory
from assistant_core.models import Message
from assistant_core.responder import TemplateResponder
from assistant_core.service import AssistantService


@pytest.fixture
def sample_service(tmp_path: Path) -> AssistantService:
    """Fixture khởi tạo AssistantService chuẩn dữ liệu cho các bài test."""
    offices_csv = tmp_path / "offices.csv"
    offices_csv.write_text(
        "name,room,hours\nAcademic,A101,8am-5pm\nLibrary,B202,7am-9pm\n",
        encoding="utf-8",
    )

    handbook_json = tmp_path / "handbook.json"
    handbook_json.write_text(
        '[{"id": "R1", "title": "Thesis", "text": "Thesis regulations..."}]',
        encoding="utf-8",
    )

    settings = Settings(data_dir=tmp_path)
    offices = OfficeDirectory.from_csv(offices_csv)
    handbook = Handbook.from_json(handbook_json)
    responder = TemplateResponder()

    return AssistantService(
        settings=settings,
        offices=offices,
        handbook=handbook,
        responder=responder,
    )


def test_service_greeting(sample_service: AssistantService):
    res = sample_service.handle(Message(text="hello"))
    assert res.answer is not None
    assert len(res.answer) > 0


def test_service_fee(sample_service: AssistantService):
    res = sample_service.handle(Message(text="tuition for 15 credits"))
    assert res.answer is not None


def test_service_office(sample_service: AssistantService):
    res = sample_service.handle(Message(text="where is Academic office?"))
    assert "A101" in res.answer or "Academic" in res.answer


def test_service_rule(sample_service: AssistantService):
    res = sample_service.handle(Message(text="thesis regulations"))
    assert res.answer is not None
