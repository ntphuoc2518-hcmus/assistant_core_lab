from assistant_core.errors import InvalidRequest
from assistant_core.tools import parse_credits, tuition
import pytest


def test_parse_credits_valid():
    credits_val, retake_val = parse_credits("tuition for 18 credits and 2 retake")
    assert credits_val == 18
    assert retake_val == 2


def test_tuition_calculation():
    total = tuition(
        credits=18,
        retake=2,
        rate=500000,
        retake_multiplier=1.5,
        max_credits=30
    )
    # 18 * 500,000 + 2 * 500,000 * 1.5 = 9,000,000 + 1,500,000 = 10,500,000
    assert total == 10500000


def test_tuition_invalid_credits():
    with pytest.raises(InvalidRequest):
        tuition(
            credits=0,
            retake=0,
            rate=500000,
            retake_multiplier=1.5,
            max_credits=30
        )