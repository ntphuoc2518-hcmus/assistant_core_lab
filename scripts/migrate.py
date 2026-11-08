"""Apply numbered SQL migrations to a SQLite database, once each.

Usage:
    python scripts/migrate.py [assistant.db]

Applied file names are remembered in the ``schema_migrations`` table, so running the
script twice is safe. Each file runs in its own transaction: it is applied completely or not at all.
Statements are split on ";", so migration files must not use ";" inside comments or string literals.
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

MIGRATIONS_DIR = Path(__file__).resolve().parent.parent / "sql" / "migrations"


def migrate(db_path: str | Path, migrations_dir: Path = MIGRATIONS_DIR) -> list[str]:
    """Apply pending migrations in name order and return the names that were applied now."""
    applied_now: list[str] = []
    con = sqlite3.connect(db_path, isolation_level=None)  # we manage transactions explicitly
    try:
        con.execute("PRAGMA foreign_keys=ON")
        con.execute(
            "CREATE TABLE IF NOT EXISTS schema_migrations ("
            " name TEXT PRIMARY KEY,"
            " applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)"
        )
        done = {row[0] for row in con.execute("SELECT name FROM schema_migrations")}
        for path in sorted(migrations_dir.glob("*.sql")):
            if path.name in done:
                continue
            statements = [s.strip() for s in path.read_text(encoding="utf-8").split(";") if s.strip()]
            con.execute("BEGIN")
            try:
                for stmt in statements:
                    con.execute(stmt)
                con.execute("INSERT INTO schema_migrations (name) VALUES (?)", (path.name,))
                con.execute("COMMIT")
            except sqlite3.Error:
                con.execute("ROLLBACK")
                raise
            applied_now.append(path.name)
    finally:
        con.close()
    return applied_now


def main(argv: list[str]) -> int:
    db_path = argv[1] if len(argv) > 1 else "assistant.db"
    applied = migrate(db_path)
    for name in applied:
        print(f"apply {name}")
    if not applied:
        print("up to date")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
