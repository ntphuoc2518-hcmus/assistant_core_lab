import math
from collections import Counter
from typing import Any


def analyse(pairs: list[tuple[str, float]]) -> dict[str, Any]:
    """Analyse route access pairs and calculate counts and p95 latencies.

    Args:
        pairs: List of tuples containing (route, latency_ms).

    Returns:
        Dict containing counts (Counter), p95 latencies dict, and max_p95_route.
    """
    if not pairs:
        return {
            "counts": Counter(),
            "p95": {},
            "max_p95_route": None,
        }

    counts: Counter = Counter()
    route_latencies: dict[str, list[float]] = {}

    for route, latency in pairs:
        counts[route] += 1
        route_latencies.setdefault(route, []).append(latency)

    p95_dict: dict[str, float] = {}
    for route, latencies in route_latencies.items():
        sorted_lats = sorted(latencies)
        # Tính chỉ số p95 (nearest rank method)
        idx = math.ceil(0.95 * len(sorted_lats)) - 1
        p95_dict[route] = sorted_lats[max(0, idx)]

    max_p95_route = max(p95_dict, key=lambda k: p95_dict[k]) if p95_dict else None

    return {
        "counts": counts,
        "p95": p95_dict,
        "max_p95_route": max_p95_route,
    }