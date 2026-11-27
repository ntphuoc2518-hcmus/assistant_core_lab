from .guard import is_vietnamese_input
from .models import Intent

GREETINGS = frozenset({"hi", "hello", "hey", "xin chao"})


def route(text: str, office_names: set[str]) -> Intent:
    """Route user message to appropriate Intent.

    Lab 8 mitigation #3 (bonus): Vietnamese messages are detected early so the
    service can respond with a targeted 'Please ask in English' reply instead of
    an unhelpful generic escalation.
    """
    t = text.lower().strip().rstrip("?!.")

    if t in GREETINGS:
        return Intent.GREETING

    # Bonus: flag Vietnamese-language input before any RAG/LLM call
    if is_vietnamese_input(text) and t not in GREETINGS:
        return Intent.UNKNOWN  # service layer maps UNKNOWN → VIETNAMESE_REPLY

    if "fee" in t or "tuition" in t:
        return Intent.FEE

    if any(name in t for name in office_names):
        return Intent.OFFICE

    return Intent.RULE
