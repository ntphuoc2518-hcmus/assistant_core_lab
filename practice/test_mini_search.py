from mini_search import DOCS, build_index, search, tokenize


def test_tokenize():
    assert tokenize("I lost my student card!") == [
        "lost",
        "student",
        "card",
    ]


def test_build_index():
    index = build_index(DOCS)

    assert index["thesis"] == {"D1"}
    assert index["credits"] == {"D1", "D2"}
    assert index["card"] == {"D3"}


def test_search_ranking():
    index = build_index(DOCS)

    assert search(index, "how many credits for a thesis") == [
        ("D1", 2),
        ("D2", 1),
    ]


def test_search_no_match():
    index = build_index(DOCS)

    assert search(index, "what is the capital of France") == []
