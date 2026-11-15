import json
from pathlib import Path

import pytest

from assistant_core.errors import ProviderError
from assistant_core.llm import StubLLM, parse_draft
from assistant_core.rag.answerer import RagAnswerer
from assistant_core.rag.chunker import load_folder
from assistant_core.rag.index import make_index


@pytest.fixture(scope="module")
def index():
    return make_index("bm25", load_folder(Path("data/kb")))


def test_a1_abstains_when_nothing_matches(index):
    res = RagAnswerer(index, None, min_score=2.0).answer(
        "what is the capital of France"
    )

    assert res.path == "abstain"
    assert res.escalate is True

def test_a1_abstains_when_score_is_too_low(index):
    res = RagAnswerer(
        index,
        None,
        min_score=100
    ).answer("can I register my thesis with 118 credits")

    assert res.path == "abstain"
    assert res.escalate is True

class CountingLLM:
    name = "counting"

    def __init__(self):
        self.calls = 0

    def complete(self, prompt: str) -> str:
        self.calls += 1
        return ""

def test_a1_does_not_call_llm_when_nothing_matches(index):
    llm = CountingLLM()

    res = RagAnswerer(
        index,
        llm,
        min_score=2.0
    ).answer("what is the capital of France")

    assert res.path == "abstain"
    assert res.escalate is True
    assert llm.calls == 0

def test_a2_citation_unknown_source_rejected():
    raw = json.dumps({
        "answer": "You can register your thesis.",
        "source_ids": ["H26#9.9"],
        "confidence": 0.9,
        "abstain": False
    })

    with pytest.raises(ProviderError):
        parse_draft(raw, {"H26#5.3"})


def test_a2_citation_missing_rejected():
    raw = json.dumps({
        "answer": "You can register your thesis.",
        "source_ids": [],
        "confidence": 0.9,
        "abstain": False
    })

    with pytest.raises(ProviderError):
        parse_draft(raw, {"H26#5.3"})


def test_a2_citation_valid_accepted():
    raw = json.dumps({
        "answer": "You can register your thesis.",
        "source_ids": ["H26#5.3"],
        "confidence": 0.9,
        "abstain": False
    })

    draft = parse_draft(raw, {"H26#5.3"})

    assert draft.source_ids == ["H26#5.3"]

def test_d5_stub_llm_success():
    index = make_index("bm25", load_folder(Path("data/kb")))

    llm = StubLLM()

    res = RagAnswerer(
        index,
        llm
    ).answer("can I register my thesis with 118 credits")

    assert res.path == "llm"
    assert any(s.id == "H26#5.3" for s in res.sources)


def test_d5_stub_llm_garbage_fallback():
    index = make_index("bm25", load_folder(Path("data/kb")))

    llm = StubLLM(garbage=True)

    res = RagAnswerer(
        index,
        llm
    ).answer("can I register my thesis with 118 credits")

    assert res.path == "retrieval"
    assert res.degraded is True


def test_d5_stub_llm_fail_fallback():
    index = make_index("bm25", load_folder(Path("data/kb")))

    llm = StubLLM(fail=True)

    res = RagAnswerer(
        index,
        llm
    ).answer("can I register my thesis with 118 credits")

    assert res.path == "retrieval"
    assert res.degraded is True