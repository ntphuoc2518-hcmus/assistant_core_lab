from members.NguyenTheHungCLC.w3.cli import run_cli


def test_cli_missing_file():
    assert run_cli([]) == 1


def test_cli_file_not_found():
    assert run_cli(["non_existent_file.csv"]) == 1


def test_cli_valid_with_today(tmp_path):
    test_file = tmp_path / "sample.csv"
    test_file.write_text("task,due\nMath,2026-10-30")

    assert run_cli([str(test_file), "--today", "2026-10-23"]) == 0