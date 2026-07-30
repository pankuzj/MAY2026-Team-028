"""FastAPI application entry point.

Task S1-F07. Responsibility: build the FastAPI app (app factory), attach
middleware, include the versioned API router, and register exception handlers.

Keep this file thin — no business logic and no route definitions here.

Why an app *factory* (``create_app()``) rather than a module-level ``app = FastAPI()``:
tests can build a fresh, independently-configured app per test module instead of
mutating one global. The module-level ``app`` at the bottom exists only because
``uvicorn app.main:app`` needs an importable target.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging
from app.middleware.request_context import RequestContextMiddleware

__all__ = ["app", "create_app"]

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown work.

    Replaces the deprecated ``@app.on_event("startup")`` decorators. Code before
    ``yield`` runs once at startup, code after it once at shutdown.

    Creating ``upload_dir`` here rather than at import time means importing
    ``app.main`` has no filesystem side effects — which matters because Alembic,
    pytest collection, and ``--help`` all import this module.
    """
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    logger.info(
        "%s starting: env=%s docs=%s uploads=%s",
        settings.project_name,
        settings.env,
        "on" if settings.docs_enabled else "off",
        settings.upload_dir.resolve(),
    )
    yield
    logger.info("%s shutting down", settings.project_name)


def create_app() -> FastAPI:
    """Build and return a fully wired FastAPI application."""
    configure_logging(settings.log_level)

    app = FastAPI(
        title=settings.project_name,
        version="0.1.0",
        description=(
            "SmartSweep — civic waste-management API. "
            "Citizens report waste issues; supervisors triage and assign crews, "
            "vehicles, and equipment; crews resolve and close them."
        ),
        # Disabled in production: /docs is a full interactive client for every
        # endpoint, including admin ones. Fine for a demo, not for a deployment.
        docs_url="/docs" if settings.docs_enabled else None,
        redoc_url="/redoc" if settings.docs_enabled else None,
        openapi_url="/openapi.json" if settings.docs_enabled else None,
        lifespan=lifespan,
    )

    # --- Middleware -------------------------------------------------------
    # Order matters and is counter-intuitive: middleware added *last* sits
    # *outermost*, so it sees the request first and the response last. CORS is
    # added last so it wraps everything below and attaches its headers to the
    # 4xx envelopes our exception handlers produce.
    #
    # Known limitation: Starlette's ServerErrorMiddleware sits outside *all*
    # user middleware, so a 500 from the catch-all handler is returned without
    # CORS headers. The browser then surfaces it as a CORS failure rather than
    # as the 500 it is. Read the real status from the server log (grep the
    # request id) — do not chase a phantom CORS misconfiguration.
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        # Without this the browser hides X-Request-ID from JS, so the frontend
        # could not put the id into an error toast.
        expose_headers=["X-Request-ID"],
    )

    # --- Error handling ---------------------------------------------------
    register_exception_handlers(app)

    # --- Routes -----------------------------------------------------------
    app.include_router(health_router)  # unversioned: /health/live, /health/ready
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    return app


app = create_app()
