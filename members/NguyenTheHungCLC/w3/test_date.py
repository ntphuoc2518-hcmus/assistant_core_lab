import sys
from datetime import date
from pathlib import Path

import pytest

# Tự động thêm thư mục gốc dự án vào đường dẫn import của Python
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from members.NguyenTheHungCLC.w3.dates import parse_due


def test_parse_due():
    today = date(2026, 10, 23)  # Thứ Sáu (Fri)

    assert parse_due("2026-10-25", today) == date(2026, 10, 25)
    assert parse_due("tomorrow", today) == date(2026, 10, 24)
    assert parse_due("in 3 days", today) == date(2026, 10, 26)
    assert parse_due("Fri", today) == date(2026, 10, 30)

    with pytest.raises(ValueError):
        parse_due("invalid date", today)