import re
from datetime import date, timedelta


def parse_due(text: str, today: date) -> date:
    """Parse a due date string into a date object.

    Supported formats:
    - YYYY-MM-DD
    - "tomorrow"
    - "in N days"
    - Weekday name (e.g., "Mon", "Fri")
    """
    text = text.strip()

    # 1. Định dạng YYYY-MM-DD
    try:
        return date.fromisoformat(text)
    except ValueError:
        pass

    # 2. Chuỗi "tomorrow"
    if text.lower() == "tomorrow":
        return today + timedelta(days=1)

    # 3. Chuỗi "in N days"
    match = re.match(r"^in\s+(\d+)\s+days?$", text, re.IGNORECASE)
    if match:
        days = int(match.group(1))
        return today + timedelta(days=days)

    # 4. Tên thứ (ví dụ: "Fri") -> Lần tiếp theo
    weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    text_cap = text.capitalize()
    if text_cap in weekdays:
        target_weekday = weekdays.index(text_cap)
        current_weekday = today.weekday()
        days_ahead = (target_weekday - current_weekday) % 7
        if days_ahead == 0:
            days_ahead = 7  # Nếu hôm nay là Fri thì Fri nghĩa là thứ 6 tuần sau
        return today + timedelta(days=days_ahead)

    raise ValueError(f"Invalid date format: {text!r}")