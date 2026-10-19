from pathlib import Path

import pytest

from assistant_core.config import Settings
from assistant_core.knowledge import Handbook, OfficeDirectory
from assistant_core.responder import StubLLMResponder
from assistant_core.service import AssistantService


@pytest.fixture
def settings() -> Settings:
    """Provide default test configuration settings."""
    return Settings(
        data_dir=Path("data"),
        llm_provider="stub",
        credit_rate_vnd=450_000,
        retake_multiplier=1.5,
        max_credits=30,
        log_level="INFO",
    )


@pytest.fixture
def offices(settings: Settings) -> OfficeDirectory:
    """Load office directory from CSV data file."""
    offices_path = settings.data_dir / "offices.csv"
    return OfficeDirectory.from_csv(offices_path)


@pytest.fixture
def handbook(settings: Settings) -> Handbook:
    """Load handbook rules from JSON data file."""
    handbook_path = settings.data_dir / "handbook.json"
    return Handbook.from_json(handbook_path)


@pytest.fixture
def responder() -> StubLLMResponder:
    """Provide a default Stub LLM responder that does not fail."""
    return StubLLMResponder(fail=False)


@pytest.fixture
def service(
    settings: Settings,
    offices: OfficeDirectory,
    handbook: Handbook,
    responder: StubLLMResponder,
) -> AssistantService:
    """Provide an AssistantService instance with injected dependencies."""
    return AssistantService(
        settings=settings,
        offices=offices,
        handbook=handbook,
        responder=responder,
    )
