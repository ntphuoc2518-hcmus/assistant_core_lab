"""Handbook.search must match whole words, not letters inside words (C04 regression)."""

import pytest

from assistant_core.knowledge import Handbook, Rule
from assistant_core.models import Intent, Message


@pytest.mark.parametrize(
    ("question", "rule_id"),
    [
        ("thesis regulations", "H26-5.3"),  # C04: used to return H26-4.2 because "a" is inside "regulations"
        ("late thesis registration", "H26-5.4"),
        ("can I register my thesis with 118 credits", "H26-5.3"),
        ("I missed my exam", "H26-7.2"),
        ("how many credits can I take", "H26-6.1"),
        ("retake a course", "H26-4.2"),
    ],
)
def test_search_picks_matching_rule(handbook, question, rule_id):
    rule = handbook.search(question)
    assert rule is not None and rule.id == rule_id


@pytest.mark.parametrize("question", ["what is the capital of France", "xyz", "a"])
def test_search_returns_none_when_nothing_matches(handbook, question):
    assert handbook.search(question) is None


def test_search_prefers_more_matching_words():
    hb = Handbook([Rule("R1", "Thesis registration", "..."), Rule("R2", "Late thesis registration", "...")])
    assert hb.search("late thesis registration").id == "R2"
    assert hb.search("thesis registration").id == "R1"  # tie -> first listed


def test_search_empty_handbook():
    assert Handbook([]).search("thesis") is None


def test_service_without_rag_says_unknown_for_unmatched_rule_question(service):
    res = service.handle(Message(text="what is the capital of France"))
    assert res.intent is Intent.UNKNOWN and res.sources == []
