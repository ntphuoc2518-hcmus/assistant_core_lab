import re

DOCS = {
    "D1": "Students may register a thesis with at least 120 credits and a GPA of 2.0.",
    "D2": "Retake credits are charged at 1.5 times the normal credit rate.",
    "D3": "A lost student card can be replaced at Student Affairs in room I.102.",
    "D4": "Students may borrow up to 5 books from the library for 14 days.",
}

STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "can",
    "for", "from", "how", "i", "in", "is", "it", "may", "my",
    "of", "on", "the", "to", "up", "what", "when", "where",
    "who", "with",
}


def tokenize(text: str) -> list[str]:
    words = re.findall(r"[a-z]+", text.lower())
    return [word for word in words if word not in STOP_WORDS]


def build_index(docs: dict[str, str]) -> dict[str, set[str]]:
    index: dict[str, set[str]] = {}

    for doc_id, text in docs.items():
        for word in tokenize(text):
            index.setdefault(word, set()).add(doc_id)

    return index


def search(
    index: dict[str, set[str]],
    query: str,
    k: int = 2,
) -> list[tuple[str, int]]:
    scores: dict[str, int] = {}

    for word in tokenize(query):
        for doc_id in index.get(word, set()):
            scores[doc_id] = scores.get(doc_id, 0) + 1

    ranked_results = sorted(
        scores.items(),
        key=lambda item: (-item[1], item[0]),
    )

    return ranked_results[:k]
