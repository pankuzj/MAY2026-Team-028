"""Shared pytest fixtures.

Task S1-F11 (owner: Jatin). **Published fixture-names-first**, for the same reason
as ``app/api/deps.py``: every ``tests/`` module depends on these names, so they
exist before the bodies do.

Working now: ``test_settings``, ``db_engine``, ``db``, ``app``, ``client``.
Stubbed for Jatin to fill once models and auth land: ``seed_ward``,
``seed_complaint``, ``citizen_token``, ``crew_token``, ``admin_token``,
``citizen_client``, ``crew_client``, ``admin_client``.

Test database strategy (plan section 14): SQLite in memory for unit and API
tests, because they are the ones run on every save and must stay fast. Only
``tests/integration`` talks to real PostgreSQL, via the ``integration`` marker.
"""

import os

# ---------------------------------------------------------------------------
# This block MUST run before any `app.*` import.
#
# `app.core.config` builds its Settings singleton at import time, and
# `app.db.session` builds the engine from it at import time too. By the time
# a fixture body runs it is far too late to change the URL — the engine would
# already be pointed at the developer's real PostgreSQL database, and a test
# that calls create_all()/drop_all() would then wipe local dev data.
#
# setdefault, not assignment: CI overrides DATABASE_URL for the integration job.
# ---------------------------------------------------------------------------
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("ENV", "test")
os.environ.setdefault("JWT_SECRET_KEY", "test-only-secret-not-used-anywhere-real")
os.environ.setdefault("LOG_LEVEL", "WARNING")  # keep test output readable

from collections.abc import Generator  # noqa: E402

import pytest  # noqa: E402
from fastapi import FastAPI  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.core.config import Settings, get_settings  # noqa: E402
from app.db.base_models import Base  # noqa: E402
from app.db.session import SessionLocal, engine  # noqa: E402


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    """The Settings object the app under test is using."""
    return get_settings()


@pytest.fixture(scope="session")
def db_engine(test_settings: Settings):
    """Create the schema once per test session, drop it at the end.

    Session-scoped because CREATE TABLE for sixteen tables per test would
    dominate the runtime. Per-test *isolation* is handled by the ``db`` fixture
    below rolling back, not by rebuilding the schema.

    ``Base`` is imported from ``db.base_models``, not ``db.base`` — that is the
    module which imports every model, so this is what makes the tables exist.
    """
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db(db_engine) -> Generator[Session, None, None]:
    """A transactional session that is rolled back after each test.

    The pattern: open a connection, begin a transaction, bind the session to that
    connection, and roll the whole thing back at teardown. Anything the test
    wrote — even through a service that called ``commit()`` — is discarded,
    because the service's commit only ends the inner nested transaction, not the
    outer one owned here.

    The alternative, ``drop_all``/``create_all`` per test, is correct but roughly
    two orders of magnitude slower.
    """
    connection = db_engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture()
def app(db: Session) -> FastAPI:
    """The FastAPI app with its DB dependency pointed at the test session.

    Built per test via ``create_app()`` so a test that mutates app state cannot
    leak into the next one. The dependency override is the important part: without
    it the routes would open their own sessions through ``get_db`` and would not
    see the rows this test inserted, nor be rolled back with it.
    """
    from app.api.deps import get_db
    from app.main import create_app

    application = create_app()

    def _override_get_db() -> Generator[Session, None, None]:
        yield db

    application.dependency_overrides[get_db] = _override_get_db
    return application


@pytest.fixture()
def client(app: FastAPI) -> Generator[TestClient, None, None]:
    """Unauthenticated HTTP client.

    ``TestClient`` runs the real ASGI app in-process — no server, no port, no
    network. Same code path in CI as locally.

    ``raise_server_exceptions=False`` makes the client return the 500 our
    catch-all handler produced instead of re-raising the exception into the test.
    That is what lets us assert on the error envelope for unexpected failures.
    """
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client


# ---------------------------------------------------------------------------
# Stubs below — names are final, bodies belong to S1-F11 (Jatin) and land once
# the models (S1-M01/M02/M04) and auth service (S1-S01) exist. Every test author
# can already write `def test_x(admin_client, seed_complaint):` today.
# ---------------------------------------------------------------------------


@pytest.fixture()
def seed_ward(db: Session):
    """One persisted Ward row. TODO(S1-F11): needs app.models.ward (S1-M01)."""
    pytest.skip("seed_ward: blocked on S1-M01 (Ward model)")


@pytest.fixture()
def seed_complaint(db: Session, seed_ward):
    """One persisted Pending complaint. TODO(S1-F11): needs S1-M02."""
    pytest.skip("seed_complaint: blocked on S1-M02 (Complaint model)")


@pytest.fixture()
def citizen_token(db: Session) -> str:
    """Signed access token for a citizen. TODO(S1-F11): needs S1-F04 + S1-M01."""
    pytest.skip("citizen_token: blocked on S1-F04 (security) and S1-M01 (User)")


@pytest.fixture()
def crew_token(db: Session) -> str:
    """Signed access token for a crew member. TODO(S1-F11)."""
    pytest.skip("crew_token: blocked on S1-F04 (security) and S1-M01 (User)")


@pytest.fixture()
def admin_token(db: Session) -> str:
    """Signed access token for an admin. TODO(S1-F11)."""
    pytest.skip("admin_token: blocked on S1-F04 (security) and S1-M01 (User)")


def _authed_client(client: TestClient, token: str) -> TestClient:
    """Attach a bearer token to every request the client makes.

    Setting the header on the client, rather than passing ``headers=`` at each
    call site, keeps the ~84 planned test cases free of auth boilerplate.
    """
    client.headers["Authorization"] = f"Bearer {token}"
    return client


@pytest.fixture()
def citizen_client(client: TestClient, citizen_token: str) -> TestClient:
    """Client authenticated as a citizen."""
    return _authed_client(client, citizen_token)


@pytest.fixture()
def crew_client(client: TestClient, crew_token: str) -> TestClient:
    """Client authenticated as a crew member."""
    return _authed_client(client, crew_token)


@pytest.fixture()
def admin_client(client: TestClient, admin_token: str) -> TestClient:
    """Client authenticated as an admin."""
    return _authed_client(client, admin_token)
