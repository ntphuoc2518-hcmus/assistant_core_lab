"""Migrations are repeatable and produce a schema the Repository can use."""

import importlib.util
import sqlite3
from pathlib import Path

import pytest

from assistant_api.db import Repository, init_db, make_engine

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("migrate", ROOT / "scripts" / "migrate.py")
migrate_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(migrate_mod)


def tables(db_file: Path) -> set[str]:
    con = sqlite3.connect(db_file)
    try:
        return {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
    finally:
        con.close()


def test_migrate_is_repeatable(tmp_path):
    db_file = tmp_path / "assistant.db"
    assert migrate_mod.migrate(db_file) == ["001_init.sql"]
    assert migrate_mod.migrate(db_file) == []  # second run is a no-op
    assert {"chat_session", "interaction", "feedback", "schema_migrations"} <= tables(db_file)


def test_migrated_schema_works_with_repository(tmp_path):
    db_file = tmp_path / "assistant.db"
    migrate_mod.migrate(db_file)
    engine = make_engine(f"sqlite:///{db_file}")
    init_db(engine)  # must not fail or duplicate anything on a migrated database
    repo = Repository(engine, "salt")
    repo.record_interaction("s", "req-1", "rule", "H26-5.3", True, False, 3.0)
    assert repo.add_feedback("req-1", 0, None) is not None
    assert repo.add_feedback("missing", 1, None) is None
    engine.dispose()


def test_migration_after_app_created_tables(tmp_path):
    """The app may have created the tables first; the migration must still apply safely."""
    db_file = tmp_path / "assistant.db"
    engine = make_engine(f"sqlite:///{db_file}")
    init_db(engine)
    engine.dispose()
    assert migrate_mod.migrate(db_file) == ["001_init.sql"]
    assert migrate_mod.migrate(db_file) == []


def test_migration_check_constraint(tmp_path):
    db_file = tmp_path / "assistant.db"
    migrate_mod.migrate(db_file)
    con = sqlite3.connect(db_file)
    try:
        con.execute("PRAGMA foreign_keys=ON")
        con.execute("INSERT INTO chat_session (id, channel, created_at) VALUES ('h', 'web', '2026-01-01')")
        con.execute(
            "INSERT INTO interaction (request_id, session_id, intent, created_at) "
            "VALUES ('r', 'h', 'fee', '2026-01-01')"
        )
        with pytest.raises(sqlite3.IntegrityError):  # rating 7 is refused by the CHECK constraint
            con.execute("INSERT INTO feedback (request_id, rating, created_at) VALUES ('r', 7, '2026-01-01')")
        with pytest.raises(sqlite3.IntegrityError):  # feedback for an unknown request is refused by the FK
            con.execute("INSERT INTO feedback (request_id, rating, created_at) VALUES ('ghost', 1, '2026-01-01')")
    finally:
        con.close()
