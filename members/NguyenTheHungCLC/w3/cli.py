import argparse
import sys
from datetime import date
from pathlib import Path

from members.NguyenTheHungCLC.w3.dates import parse_due


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the ArgumentParser for CLI."""
    parser = argparse.ArgumentParser(description="Study Planner CLI")
    parser.add_argument(
        "file",
        type=str,
        nargs="?",
        default=None,
        help="Path to the input CSV file",
    )
    parser.add_argument(
        "--today",
        type=str,
        default=None,
        help="Base date in YYYY-MM-DD or relative format",
    )
    return parser


def run_cli(args: list[str] | None = None) -> int:
    """Parse arguments and execute CLI commands.

    Returns:
        Exit code: 0 for success, 1 for error.
    """
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    # Kiểm tra trường hợp thiếu tham số file
    if not parsed_args.file:
        print("Lỗi: Thiếu tham số đường dẫn tệp (file).", file=sys.stderr)
        return 1

    file_path = Path(parsed_args.file)
    if not file_path.exists():
        print(f"Lỗi: Tệp '{parsed_args.file}' không tồn tại.", file=sys.stderr)
        return 1

    # Xử lý ngày --today
    today_val = date.today()
    if parsed_args.today:
        try:
            today_val = parse_due(parsed_args.today, date.today())
        except ValueError as err:
            print(f"Lỗi định dạng --today: {err}", file=sys.stderr)
            return 1

    print(f"Đã nạp tệp '{file_path}' với ngày mốc: {today_val}")
    return 0


def main() -> None:
    """Entry point for command line execution."""
    exit_code = run_cli()
    if exit_code != 0:
        sys.exit(exit_code)


if __name__ == "__main__":
    main()