"""Deterministic guardrails that run BEFORE retrieval or any LLM call."""

from __future__ import annotations

import re

PRIVATE_PATTERNS = [
    r"\b(my|a) (friend|classmate|roommate)'?s?\b.*\b(grade|score|gpa|result|phone|address)",
    r"\b(grade|score|gpa|result|phone|address)s?\b.*\b(of|for) (another|other) student",
    r"\b(grade|score|gpa|result|phone|address)s?\b.*\b(my|a) (friend|classmate|roommate)",
    r"\b\d{8}\b",  # looks like a student id
    # Lab 8 mitigation #3: catch "of student <name>" privacy pattern (partner finding X03)
    r"\b(phone|gpa|grade|score|address)\b.*\bof student\b",
    r"\bof student\b.*\b(phone|gpa|grade|score|address)\b",
]


def is_private_request(text: str) -> bool:
    t = text.lower()
    return any(re.search(p, t) for p in PRIVATE_PATTERNS)


PRIVATE_REPLY = "I can't share information about other students. You can only see your own records after logging in."

# ---------------------------------------------------------------------------
# Lab 8 mitigation #3 (bonus): Vietnamese-language detection
# If the user writes in Vietnamese, reply with a polite redirect instead of
# escalating generically. Only trigger when the message contains Vietnamese
# diacritics AND does NOT already match a supported English keyword.
# ---------------------------------------------------------------------------

_VIET_CHARS = re.compile(
    r"[àáâãèéêìíòóôõùúýăđơư"
    r"ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚÝĂĐƠƯ"
    r"ạảấầẩẫậắằẳẵặẹẻẽếềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹ"
    r"ẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼẾỀỂỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪỬỮỰỲỴỶỸ]"
)

VIETNAMESE_REPLY = (
    "Please ask in English — this assistant currently only supports English. "
    "For further help, contact the student support office."
)


def is_vietnamese_input(text: str) -> bool:
    """Return True when the text appears to be Vietnamese (has diacritics)."""
    return bool(_VIET_CHARS.search(text))
