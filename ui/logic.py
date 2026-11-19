"""UI logic without Streamlit, so it can be unit-tested."""

from __future__ import annotations

from ui.api_client import ChatResult

WELCOME = (
    "Hi! I can answer questions about fees, offices and the student handbook. "
    "Try: “Can I register my thesis with 118 credits?”"
)
EXAMPLES = [
    "Can I register my thesis with 118 credits?",
    "Tuition for 18 credits and 2 retake",
    "Where is the library?",
    "I lost my student card",
]


def validate_input(text: str) -> str | None:
    """Return an error message for bad input, or None if it is fine."""
    t = text.strip()
    if not t:
        return "Please type a question."
    if len(t) > 2000:
        return "Your question is too long (max 2000 characters)."
    return None


def format_sources(sources: list[dict]) -> str:
    """Nicer source display: title first with chunk-ID in parentheses.

    Example:
        "📄 5.3 Thesis registration (H26#5.3); 📄 6.1 GPA rules (H26#6.1)"
    Returns '' when there are no sources.
    """
    if not sources:
        return ""
    parts = [f"📄 {s['title']} ({s['id']})" for s in sources]
    return "Sources: " + "; ".join(parts)


def status_note(result: ChatResult) -> str | None:
    """A short note shown under the answer, explaining special situations."""
    # TODO L2 (5 lines): [DONE]
    if result.escalate:
        return "I could not find this in the official documents. A staff member can help: Training Office, room I.101."
    elif result.degraded:
        return "Shown directly from the source document (the AI helper was unavailable)."
    return None
