from collections import Counter

from members.NguyenTheHungCLC.w3.log_stats import analyse


def test_analyse_basic():
    pairs = [
        ("/api/v1/health", 10.0),
        ("/api/v1/tasks", 100.0),
        ("/api/v1/tasks", 200.0),
        ("/api/v1/health", 15.0),
    ]

    result = analyse(pairs)

    assert result["counts"] == Counter({"/api/v1/health": 2, "/api/v1/tasks": 2})
    assert "/api/v1/tasks" in result["p95"]
    assert result["max_p95_route"] == "/api/v1/tasks"


def test_analyse_empty():
    result = analyse([])
    assert result["counts"] == Counter()
    assert result["p95"] == {}
    assert result["max_p95_route"] is None