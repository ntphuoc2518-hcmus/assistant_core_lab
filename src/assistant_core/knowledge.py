import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path

from .errors import DataError

# Words too common to say which rule a question is about.
_STOP = frozenset({"a", "an", "the", "of", "to", "in", "on", "for", "and", "or", "my", "i", "is", "can", "do", "how"})


def _words(text: str) -> set[str]:
    """Whole lowercase words, minus stop words, with a plural "s" removed ("credits" -> "credit")."""
    words = re.findall(r"\w+", text.lower())
    return {w[:-1] if len(w) > 4 and w.endswith("s") else w for w in words if w not in _STOP}


@dataclass(frozen=True)
class Office:
    name: str
    room: str
    hours: str


class OfficeDirectory:
    def __init__(self, offices: dict[str, Office]):
        self._offices = offices

    @classmethod
    def from_csv(cls, path: Path) -> "OfficeDirectory":
        try:
            with path.open(encoding="utf-8", newline="") as f:
                rows = list(csv.DictReader(f))
        except FileNotFoundError as exc:
            raise DataError(f"office file not found: {path}") from exc

        return cls({r["name"].lower(): Office(r["name"], r["room"], r["hours"]) for r in rows})

    @property
    def names(self) -> set[str]:
        return set(self._offices)

    def find(self, text: str) -> Office | None:
        t = text.lower()
        return next((o for name, o in self._offices.items() if name in t), None)


@dataclass(frozen=True)
class Rule:
    id: str
    title: str
    text: str


class Handbook:
    def __init__(self, rules: list[Rule]):
        self._rules = rules

    @classmethod
    def from_json(cls, path: Path) -> "Handbook":
        try:
            with path.open(encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError as exc:
            raise DataError(f"handbook file not found: {path}") from exc

        rules = [Rule(id=r["id"], title=r["title"], text=r["text"]) for r in data]
        return cls(rules)

    def search(self, text: str) -> Rule | None:
        """Return the rule whose title shares the most whole words with ``text``, or None if none match.

        Ties go to the rule listed first in the handbook.
        """
        query = _words(text)
        best, best_score = None, 0
        for rule in self._rules:
            score = len(query & _words(rule.title))
            if score > best_score:
                best, best_score = rule, score
        return best
