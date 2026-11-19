import httpx

from ui.api_client import AssistantClient, ChatResult
from ui.logic import format_sources, status_note, validate_input

OK = {
    "answer": "Room B.201",
    "intent": "office",
    "sources": [{"id": "S26#1", "title": "1 Library borrowing"}],
    "degraded": False,
    "escalate": False,
    "path": "deterministic",
    "request_id": "abc123",
}


def client_with(handler) -> AssistantClient:
    return AssistantClient("http://api.test", transport=httpx.MockTransport(handler))


def test_ask_ok():
    r = client_with(lambda req: httpx.Response(200, json=OK)).ask("where is the library", "s1")
    assert r.ok and r.answer == "Room B.201" and r.request_id == "abc123"


def test_ask_backend_down():
    def boom(req):
        raise httpx.ConnectError("refused", request=req)

    r = client_with(boom).ask("hi", "s1")
    assert not r.ok and "backend" in r.error


def test_ask_validation_and_server_errors():
    assert "type a question" in client_with(lambda req: httpx.Response(422)).ask("", "s").error
    assert "error 500" in client_with(lambda req: httpx.Response(500)).ask("x", "s").error


def test_feedback():
    assert client_with(lambda req: httpx.Response(201, json={})).send_feedback("abc123", 1)


def test_validate_input():
    assert validate_input("   ") == "Please type a question."
    assert validate_input("x" * 2001).startswith("Your question is too long")
    assert validate_input("hello") is None


def test_format_sources():
    assert format_sources([]) == ""
    # Bonus: nicer display — title first, ID in parentheses, with 📄 emoji
    result = format_sources(OK["sources"])
    assert result == "Sources: 📄 1 Library borrowing (S26#1)"


def test_format_sources_multiple():
    sources = [
        {"id": "H26#5.3", "title": "5.3 Thesis registration"},
        {"id": "H26#6.1", "title": "6.1 GPA requirements"},
    ]
    result = format_sources(sources)
    assert result.startswith("Sources:")
    assert "📄 5.3 Thesis registration (H26#5.3)" in result
    assert "📄 6.1 GPA requirements (H26#6.1)" in result


# ---- E.2: Emoji and Unicode input must not crash validate_input or the client ----

def test_e2_emoji_input_accepted():
    """E.2 — emoji characters must pass validate_input (not too long, not empty)."""
    assert validate_input("What about 😊 requirements for GPA?") is None
    assert validate_input("🎓📚 deadline thesis") is None


def test_e2_vietnamese_input_accepted():
    """E.2 — Vietnamese diacritics must pass validate_input."""
    assert validate_input("học phí 15 tín chỉ") is None
    assert validate_input("Thời gian đăng ký luận văn là khi nào?") is None


def test_e2_smart_quotes_accepted():
    """E.2 — smart / curly quotes must pass validate_input."""
    assert validate_input("\u201cCan I register thesis today?\u201d") is None


def test_e2_multiple_emoji_sequences_accepted():
    """E.2 — multiple consecutive emoji must not exceed length erroneously."""
    text = "🎓" * 10 + " when is thesis deadline?"
    assert validate_input(text) is None


def test_e2_emoji_sent_to_api():
    """E.2 — emoji payload must be forwarded to the API unchanged (JSON-safe encoding)."""
    received: list[bytes] = []

    def capture(req: httpx.Request) -> httpx.Response:
        received.append(req.content)
        return httpx.Response(200, json={**OK, "answer": "ok"})

    client_with(capture).ask("🎓 thesis deadline?", "s1")
    assert len(received) == 1
    # httpx may use \uXXXX escaping or raw UTF-8 — both are valid JSON; check the decoded JSON
    import json
    parsed = json.loads(received[0].decode("utf-8"))
    assert parsed["message"] == "🎓 thesis deadline?"


def test_e2_unicode_thai_accepted():
    """E.2 — non-Latin script (Thai) must also be accepted."""
    assert validate_input("ลงทะเบียนวิทยานิพนธ์เมื่อไหร่?") is None


def test_status_note():
    assert "Training Office" in status_note(ChatResult(ok=True, escalate=True))
    assert status_note(ChatResult(ok=True)) is None
