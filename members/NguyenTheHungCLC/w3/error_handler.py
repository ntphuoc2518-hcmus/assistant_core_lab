from pathlib import Path
from typing import NoReturn


class InfeasiblePlanError(Exception):
    """Ngoại lệ khi kế hoạch học tập không khả thi."""

    pass


def handle_planner_errors(file_path_str: str) -> Path:
    """Kiểm tra và xử lý các lỗi đọc file cho Study Planner.

    Args:
        file_path_str: Đường dẫn tới file đầu vào.

    Returns:
        Path object hợp lệ nếu file tồn tại và không rỗng.

    Raises:
        FileNotFoundError: Nếu file không tồn tại.
        ValueError: Nếu file rỗng.
    """
    path = Path(file_path_str)

    # 1. Kiểm tra thiếu file
    if not path.exists():
        raise FileNotFoundError(f"Lỗi: Tệp '{file_path_str}' không tồn tại.")

    # 2. Kiểm tra file rỗng
    if path.stat().st_size == 0:
        raise ValueError(f"Lỗi: Tệp '{file_path_str}' bị rỗng.")

    return path


def raise_infeasible_plan(reason: str) -> NoReturn:
    """Bắn lỗi kế hoạch không khả thi.

    Args:
        reason: Lý do kế hoạch không thể thực hiện.
    """
    raise InfeasiblePlanError(f"Kế hoạch không khả thi: {reason}")