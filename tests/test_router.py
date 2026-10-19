
import pytest

from assistant_core.models import Intent
from assistant_core.router import route


@pytest.mark.parametrize(
    "text, expected",
    [
        ("hi", Intent.GREETING),
        ("hello", Intent.GREETING),
        ("hey", Intent.GREETING),
        ("xin chao", Intent.GREETING),
        ("  HI  ", Intent.GREETING),
        ("Hello!", Intent.GREETING),
        ("Hey?", Intent.GREETING),
    ],
)
def test_route_greetings(text, expected):
    assert route(text, set()) == expected


@pytest.mark.parametrize(
    "text",
    [
        "fee",
        "tuition",
        "What is the tuition fee?",
        "Tell me about fees",
        "TUITION",
    ],
)
def test_route_fee(text):
    assert route(text, set()) == Intent.FEE


def test_route_office():
    office_names = {"registrar", "student affairs"}

    assert route("Where is the registrar?", office_names) == Intent.OFFICE
    assert route("Contact student affairs", office_names) == Intent.OFFICE


def test_route_office_name_matching_is_case_insensitive():
    office_names = {"registrar"}

    assert route("Where is the registrar?", office_names) == Intent.OFFICE
    assert route("Where is the REGISTRAR?", office_names) == Intent.OFFICE

@pytest.mark.parametrize(
    "text",
    [
        "What are the library rules?",
        "How do I register for a course?",
        "random question",
        "",
    ],
)
def test_route_rule(text):
    assert route(text, set()) == Intent.RULE


def test_fee_has_priority_over_office():
    office_names = {"tuition"}

    assert route("tuition", office_names) == Intent.FEE
