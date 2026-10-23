import pytest
from members.NguyenTheHungCLC.w3.error_handler import (
    InfeasiblePlanError,
    handle_planner_errors,
    raise_infeasible_plan,
)


def test_missing_file():
    with pytest.raises(FileNotFoundError):
        handle_planner_errors("non_existent_tasks.csv")


def test_empty_file(tmp_path):
    empty_file = tmp_path / "empty.csv"
    empty_file.write_text("")

    with pytest.raises(ValueError, match="bị rỗng"):
        handle_planner_errors(str(empty_file))


def test_infeasible_plan():
    with pytest.raises(InfeasiblePlanError, match="Kế hoạch không khả thi"):
        raise_infeasible_plan("Tổng số giờ vượt quá giới hạn 24h")