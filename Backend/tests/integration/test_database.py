"""Integration smoke tests — real PostgreSQL, not SQLite.

Run with::

    DATABASE_URL=postgresql+psycopg://smartsweep:smartsweep@localhost:5432/smartsweep_test \\
        uv run pytest -m integration

Excluded from the default run (see ``addopts`` in pyproject.toml), so working on
a service never requires a database container.

Why these exist rather than trusting the SQLite suite: SQLite and PostgreSQL
disagree about things that matter to us — timezone-aware timestamps, ``ALTER
TABLE`` support, case-sensitive string comparison, and foreign-key enforcement
(off by default in SQLite). A suite that only ever runs on SQLite can pass while
the deployed application is broken. These tests are the tripwire for that gap.
"""

import pytest
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from app.core.config import settings

# Applies to every test in the module, so no per-test decorator is needed.
pytestmark = pytest.mark.integration


def test_is_actually_running_against_postgres() -> None:
    """Guard against the suite silently passing on SQLite.

    Without this, forgetting to set DATABASE_URL means conftest falls back to
    in-memory SQLite and the whole integration suite reports green while having
    tested nothing it was written to test.
    """
    assert not settings.is_sqlite, (
        "Integration tests require PostgreSQL. Set DATABASE_URL, e.g. "
        "postgresql+psycopg://smartsweep:smartsweep@localhost:5432/smartsweep_test"
    )


def test_connection_round_trip(db: Session) -> None:
    """The session can execute a statement and read the result back."""
    assert db.execute(text("SELECT 1")).scalar_one() == 1


def test_server_reports_a_postgres_version(db: Session) -> None:
    version = db.execute(text("SELECT version()")).scalar_one()
    assert "PostgreSQL" in version


def test_alembic_has_been_applied(db: Session) -> None:
    """``alembic upgrade head`` ran before the tests.

    The ``alembic_version`` table is created by Alembic itself on first upgrade,
    so its presence proves the migration step happened. If this fails in CI, the
    ``alembic upgrade head`` step did not run or did not target this database —
    check that both steps use the same DATABASE_URL.
    """
    assert inspect(db.get_bind()).has_table("alembic_version")


def test_timestamps_come_back_timezone_aware(db: Session) -> None:
    """``TIMESTAMPTZ`` round-trips as an aware datetime (plan assumption 8).

    This is precisely a case SQLite cannot check: it has no native timestamp type
    and hands back naive values. A naive datetime compared against an aware one
    raises TypeError, so getting this wrong breaks resolution-time arithmetic in
    the Sprint 2 reports.
    """
    result = db.execute(text("SELECT now()")).scalar_one()
    assert result.tzinfo is not None
