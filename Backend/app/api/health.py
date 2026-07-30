"""Liveness and readiness probes.

Deliberately **not** under ``/api/v1``: these are operational endpoints, not part
of the product API contract. Versioning them would imply we might one day ship a
``/api/v2/health``, which makes no sense — Docker healthchecks and CI wait-loops
need one stable URL forever.

The liveness/readiness split is the standard one:

* **live** — "is the process running?" Answers without touching anything external.
  If this fails, restarting the container is the right response.
* **ready** — "can it actually serve traffic?" Checks the database. If this fails
  but ``live`` passes, restarting will not help; the dependency is down.

Collapsing them into one endpoint means a brief database blip triggers a restart
loop of a perfectly healthy application.
"""

from typing import Any

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core.config import settings
from app.db.session import engine

__all__ = ["router"]

router = APIRouter(prefix="/health", tags=["health"])


@router.get(
    "/live",
    summary="Liveness probe",
    description="Returns 200 whenever the process is able to answer HTTP. Touches no dependencies.",
    operation_id="healthLive",
)
def liveness() -> dict[str, Any]:
    """Process is up."""
    return {"status": "ok", "service": settings.project_name, "env": settings.env}


@router.get(
    "/ready",
    summary="Readiness probe",
    description=(
        "Returns 200 when the application can serve traffic, which requires a working "
        "database connection. Returns 503 with the shared error envelope otherwise."
    ),
    operation_id="healthReady",
)
def readiness() -> Any:
    """Process is up *and* the database answers."""
    try:
        # SELECT 1 is the cheapest possible round trip that still proves the
        # connection is usable — it exercises the pool, the network, and auth
        # without depending on any table existing yet.
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001 — any failure means "not ready"
        # Imported lazily to keep this module importable without the schemas
        # package during early scaffolding.
        from app.core.logging import get_request_id
        from app.schemas.common import error_response

        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=error_response(
                "SERVICE_UNAVAILABLE",
                f"Database is not reachable: {type(exc).__name__}",
                request_id=get_request_id(),
            ),
        )

    return {"status": "ready", "database": "ok"}
