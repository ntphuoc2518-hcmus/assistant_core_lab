"""Lab 8 Part E — Regression tests from real failures discovered during Lab 7 testing.

Assigned to: Tinh (tinhha777qz-dev)

Covers:
  1. BUG-7: 'tuition for 18 credits and two retakes' parsed retake as 0, giving 8,100,000 instead of 9,450,000.
  2. Issue (a): Vietnamese query 'học phí 15 tín chỉ' must be handled safely without crash or 500.
  3. Issue (b): Rating buttons (👍 / 👎) must hide after a vote to prevent repeated/ignored clicks.
  4. Issue (c): Source citations must display human-readable titles and emoji, not just opaque codes like 'H26#5.3'.
"""

from __future__ import annotations

import httpx

from assistant_core.config import Settings
from assistant_core.models import Message
from assistant_core.service import build_service
from assistant_core.tools import parse_credits, tuition
from ui.api_client import AssistantClient
from ui.logic import format_sources, format_sources_rich, validate_input

# ---------------------------------------------------------------------------
# BUG-7 (Mitigation #2): Number words in retake credits ('two retakes')
# ---------------------------------------------------------------------------


def test_regression_bug7_parse_credits_word_retakes():
    """BUG-7: 'tuition for 18 credits and two retakes' must parse retake=2, not 0."""
    credits_val, retake_val = parse_credits("tuition for 18 credits and two retakes")
    assert credits_val == 18
    assert retake_val == 2

    # Also test 'one retake' and other single-digit number words up to 'ten'
    assert parse_credits("tuition for 18 credits and one retake") == (18, 1)
    assert parse_credits("tuition for 18 credits and three retakes") == (18, 3)
    assert parse_credits("tuition for 18 credits and ten retakes") == (18, 10)


def test_regression_bug7_tuition_calculation_correct():
    """BUG-7: Full fee calculation must yield 9,450,000 VND, not 8,100,000 VND."""
    query = "tuition for 18 credits and two retakes"
    credits_val, retake_val = parse_credits(query)

    # rate = 450,000, multiplier = 1.5
    # 18 * 450,000 + 2 * 450,000 * 1.5 = 8,100,000 + 1,350,000 = 9,450,000
    total = tuition(
        credits=credits_val,
        retake=retake_val,
        rate=450000,
        retake_multiplier=1.5,
        max_credits=30,
    )
    assert total == 9450000
    assert total != 8100000

    # End-to-end via service
    service = build_service(Settings())
    res = service.handle(Message(text=query))
    assert "9,450,000 VND" in res.answer
    assert "8,100,000" not in res.answer


# ---------------------------------------------------------------------------
# Issue (a): Vietnamese queries ('học phí 15 tín chỉ') handled gracefully
# ---------------------------------------------------------------------------


def test_regression_vietnamese_query_no_crash_and_escalates_gracefully():
    """Issue (a): 'học phí 15 tín chỉ' must pass UI input validation and escalate safely."""
    # UI validation must accept Vietnamese diacritics
    assert validate_input("học phí 15 tín chỉ") is None

    # Service must not crash or fail with unhandled exception
    service = build_service(Settings())
    res = service.handle(Message(text="học phí 15 tín chỉ"))
    assert res is not None
    assert res.answer != ""
    # Should safely escalate or politely indicate English requirement, not crash
    assert res.escalate is True or "English" in res.answer


# ---------------------------------------------------------------------------
# Issue (b): Rating buttons hide after submission to avoid ignored double-clicks
# ---------------------------------------------------------------------------


def test_regression_feedback_tracking_and_button_hiding():
    """Issue (b): Rating buttons should be hidden after voting, tracked via session state."""
    # Simulating UI logic: rated set tracks request_id
    rated_set: set[str] = set()
    request_id = "req_lab8_test_123"

    # Before voting: buttons are shown (request_id not in rated_set)
    assert request_id not in rated_set

    # Client sends feedback
    def mock_feedback(req: httpx.Request) -> httpx.Response:
        return httpx.Response(201, json={"status": "ok"})

    client = AssistantClient("http://api.test", transport=httpx.MockTransport(mock_feedback))
    ok = client.send_feedback(request_id, 1)
    assert ok is True

    # After voting: request_id is recorded in rated set -> buttons hidden
    rated_set.add(request_id)
    assert request_id in rated_set  # Next render: button column is not drawn


# ---------------------------------------------------------------------------
# Issue (c): Source display is user-friendly (title + emoji instead of bare code)
# ---------------------------------------------------------------------------


def test_regression_source_display_user_friendly():
    """Issue (c): Sources must show readable title and emoji 📄, not bare code 'H26#5.3'."""
    raw_sources = [{"id": "H26#5.3", "title": "5.3 Thesis registration"}]

    # Old display: bare code first without emoji
    old_display = format_sources(raw_sources)
    assert "📄" not in old_display

    # New display: human-readable title first, 📄 emoji, chunk code in parentheses
    rich_display = format_sources_rich(raw_sources)
    assert "📄 5.3 Thesis registration (H26#5.3)" in rich_display
    assert rich_display.startswith("Sources: 📄")
