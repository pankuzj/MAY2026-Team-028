"""Database engine, session factory, and the ``get_db`` request dependency.

Task S1-F03. One engine per process (it owns the connection pool — creating more
than one wastes connections), one Session per request.

Why one session per request: a Session is a unit of work with an identity map. If
two requests shared one, they would share uncommitted state and pending flushes.
If a single request opened several, its own reads would not see its own writes.
One-per-request is the shape FastAPI's dependency system makes natural.
"""

from collections.abc import Generator
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

__all__ = ["SessionLocal", "engine", "get_db"]


def _engine_kwargs() -> dict[str, Any]:
    """Engine options, which differ between SQLite (tests) and PostgreSQL.

    SQLite needs two workarounds:

    * ``check_same_thread=False`` — TestClient runs the ASGI app in a worker
      thread while the test body runs in the main thread. SQLite refuses
      cross-thread connection use unless this is off.
    * ``StaticPool`` — an in-memory database exists only for as long as its
      connection. The default pool opens a fresh connection per checkout, so each
      one would get its own empty database and tables would appear to vanish.

    Neither applies to PostgreSQL, which instead wants real pool tuning.
    """
    if settings.is_sqlite:
        from sqlalchemy.pool import StaticPool

        return {
            "connect_args": {"check_same_thread": False},
            "poolclass": StaticPool,
        }

    return {
        "pool_pre_ping": True,  # discard connections the DB closed while idle
        "pool_size": 5,
        "max_overflow": 10,
    }


engine = create_engine(settings.database_url, echo=settings.db_echo, **_engine_kwargs())

# expire_on_commit=False: after commit, attributes stay loaded. Without it, a
# route that commits and then serialises the object triggers a fresh SELECT per
# attribute — and raises DetachedInstanceError once the session has closed.
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    """Yield a request-scoped Session, rolling back on error and always closing.

    FastAPI dependency. ``app/api/deps.py`` re-exports it so routes have one
    import site (task S1-A08).

    Transaction policy: **services commit, this dependency does not.** A service
    knows when its unit of work is complete; a teardown hook does not. What the
    ``finally`` guarantees is that the connection returns to the pool no matter
    what — the ``rollback`` on the error path prevents a half-finished
    transaction from being handed to the next request that borrows it.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
