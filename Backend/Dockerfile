# syntax=docker/dockerfile:1
#
# SmartSweep backend image — task S1-F09.
#
# Two stages. The builder resolves and installs dependencies; the runtime stage
# copies only the finished virtualenv. uv itself, the build toolchain, and the
# package cache never reach the final image, which keeps it smaller and removes
# tools an attacker could otherwise use after a compromise.
#
# Layer order is chosen so that editing a Python file does not reinstall
# dependencies: pyproject.toml and uv.lock are copied and installed *before* the
# application source, so the expensive layer stays cached until deps change.
#
#   docker build -t smartsweep-api .
#   docker compose up --build

# --------------------------------------------------------------------------
# Stage 1 — builder
# --------------------------------------------------------------------------
FROM python:3.12-slim AS builder

# Pinned uv version: an image that silently picks up a new resolver is an image
# that stops being reproducible.
COPY --from=ghcr.io/astral-sh/uv:0.12.0 /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    # Copy rather than hardlink: the cache mount and /app are different
    # filesystems, so hardlinking fails with a warning on every build.
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

COPY pyproject.toml uv.lock ./

# --frozen: install exactly the lockfile, never re-resolve. A container that
#   quietly resolved different versions than CI tested is the classic
#   "works on my machine" bug, one layer down.
# --no-dev: pytest, ruff, and black have no business in a runtime image.
# --no-install-project: only dependencies here, so this layer stays cached when
#   application code changes.
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# --------------------------------------------------------------------------
# Stage 2 — runtime
# --------------------------------------------------------------------------
FROM python:3.12-slim AS runtime

# Run as a non-root user. If the process is compromised it cannot write outside
# what it owns, and it cannot install packages.
RUN groupadd --system --gid 1001 smartsweep \
    && useradd --system --uid 1001 --gid smartsweep --create-home smartsweep

WORKDIR /app

ENV PATH="/app/.venv/bin:$PATH" \
    # Tracebacks and log lines appear immediately instead of sitting in a buffer
    # until the container stops — the difference between debuggable and not.
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# The virtualenv is self-contained, so copying it is the entire install step.
COPY --from=builder --chown=smartsweep:smartsweep /app/.venv /app/.venv

# Application code last: the layer that changes most often is the cheapest to
# rebuild. .dockerignore keeps tests, .venv, and .env out.
COPY --chown=smartsweep:smartsweep alembic.ini ./
COPY --chown=smartsweep:smartsweep app ./app

# Photo uploads (US-03) land here. Created and owned up front because the
# non-root user cannot mkdir in / at runtime. Mount a volume over it in compose
# so uploads survive a container rebuild.
RUN mkdir -p /app/uploads && chown smartsweep:smartsweep /app/uploads

USER smartsweep

EXPOSE 8000

# Hits the readiness probe, so the container is "healthy" only once it can
# actually reach the database — not merely when the process has started.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health/ready', timeout=4).status == 200 else 1)"

# No --reload: that is a development flag, and it watches the filesystem in a
# tight loop. Compose overrides this command for local development.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
