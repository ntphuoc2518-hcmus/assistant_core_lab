"""Lab 6 warm-up: build a tiny search engine with the data structures you already know.

No AI here — just dictionaries, sets and sorting (DSA!). Run the tests:  pytest -q test_mini_search.py
"""
import re

DOCS = {
    "D1": "Students may register a thesis with at least 120 credits and a GPA of 2.0.",
    "D2": "Retake credits are charged at 1.5 times the normal credit rate.",
    "D3": "A lost student card can be replaced at Student Affairs in room I.102.",
    "D4": "Students may borrow up to 5 books from the library for 14 days.",
}
STOP = {"a", "an", "the", "at", "of", "for", "to", "in", "can", "be", "is", "my", "i", "may", "with", "and", "up", "from"}


def tokenize(text: str) -> list[str]:
    """'Lost my card!' -> ['lost', 'card']  (lower-case words, stop words removed) — given."""
    return [w for w in re.findall(r"\w+", text.lower()) if w not in STOP]


def build_index(docs: dict[str, str]) -> dict[str, set[str]]:
    index: dict[str, set[str]] = {}
    for doc_id, text in docs.items():
        for tok in tokenize(text):
            index.setdefault(tok, set()).add(doc_id)
    return index


def search(index: dict[str, set[str]], query: str) -> list[tuple[str, int]]:
    scores: dict[str, int] = {}
    for tok in tokenize(query):
        for doc_id in index.get(tok, set()):
            scores[doc_id] = scores.get(doc_id, 0) + 1
    return sorted(
        [(doc_id, score) for doc_id, score in scores.items() if score > 0],
        key=lambda kv: (-kv[1], kv[0]),
    )


