# SmartSweep — Backend

Backend for **SmartSweep**, a civic waste-management platform for reporting and
tracking garbage/waste-collection issues across three roles: **Citizen**,
**Cleanup Crew**, and **Ward Supervisor / Admin**.

This document is the shared blueprint for the team. It describes the target
architecture, what each folder is for, how the layers depend on one another,
and how we work (Git, tests, migrations, Docker, CI).

**Current phase: the foundation runs.** Dependencies are pinned and locked, config
and logging are wired, the app factory boots, the error envelope is in place,
Alembic is connected, and CI is green. Models, endpoints, and business logic are
next — every module still carrying a `# TODO` names the task ID and owner from
`../SPRINT_PLAN.md`.

**New to the repo? Jump to [Getting started](#getting-started).** For the reasoning
behind each setup decision, read `../docs/DEV_LOG.md`.

> The API contract is largely pre-negotiated by the existing React frontend
> (`../Frontend`): its context mutators were written `async` on purpose so that
> swapping their bodies for `fetch()` calls to this backend won't require
> touching UI components.

---

## Tech stack

| Concern | Choice | Pinned version |
|---|---|---|
| Language | Python | **3.12+** |
| Web framework | FastAPI | 0.115 |
| ASGI server | Uvicorn | 0.32 |
| ORM | SQLAlchemy | 2.0 |
| Database driver | psycopg 3 (`psycopg[binary]`) | 3.2 |
| Database | PostgreSQL | 16 |
| Migrations | Alembic | 1.14 |
| Validation / DTOs | Pydantic v2 + pydantic-settings | 2.10 / 2.7 |
| Auth | **PyJWT + bcrypt** | 2.10 / 4.2 |
| Testing | pytest + pytest-cov + httpx | 8.3 / 6.0 / 0.28 |
| Packaging / venv | uv | 0.12 |
| Containers | Docker + Docker Compose | — |
| Lint / format | Ruff + Black | 0.8 / 24.10 |
| Git hooks | pre-commit | 4.0 |
| CI | GitHub Actions | — |

Exact resolved versions for all 57 packages are in `uv.lock`. Two deliberate
changes from the original blueprint, both explained in `../docs/DEV_LOG.md`:

- **Python 3.12, not 3.13** — the team's machines run 3.12.3 and nothing in the
  stack needs 3.13.
- **PyJWT + bcrypt, not python-jose + passlib** — `passlib` 1.7.4 is unmaintained
  and breaks against `bcrypt>=4.1`; `python-jose` has open CVEs.

---

## Architecture principles

- Clean, layered architecture with strict separation of concerns.
- **Business logic lives in Services.** Database access lives in Repositories.
- Configuration comes only from environment variables.
- Authentication uses JWT with role-based access control (RBAC).
- Maintainability and readability over cleverness — easy for five developers
  to work on in parallel.

---

## Folder structure

```
Backend/
├── app/
│   ├── main.py                 # FastAPI app factory + router wiring (thin)
│   ├── api/                    # HTTP boundary — routing only
│   │   ├── deps.py             # get_db, get_current_user, require_role
│   │   └── v1/
│   │       ├── router.py       # aggregates all v1 routers
│   │       └── routes/         # one module per resource
│   ├── core/                   # config, security, logging, exceptions
│   ├── db/                     # engine, session, base + Alembic migrations/
│   ├── models/                 # SQLAlchemy ORM models (one file per entity)
│   ├── schemas/                # Pydantic v2 DTOs (Create/Update/Read)
│   ├── repositories/           # DB access only (one per aggregate)
│   ├── services/               # business logic (one per use-case area)
│   ├── middleware/             # request-id, logging, error handling, CORS
│   └── utils/                  # pure helpers (haversine, text sim, date math)
├── tests/
│   ├── unit/                   # services & utils (DB faked)
│   ├── integration/            # repositories against a real test DB
│   └── api/                    # endpoints via TestClient
├── pyproject.toml              # uv deps + Ruff/Black/pytest config
├── alembic.ini
├── Dockerfile
├── docker-compose.yml          # api + postgres
├── .env.example
└── .pre-commit-config.yaml
```

### Layer responsibilities

- **`app/main.py`** — App factory: create the app, attach middleware, include
  the versioned router, register exception handlers. No logic, no routes.
- **`api/`** — HTTP boundary. Routes parse a request, call a service, and return
  a schema. No DB access, no business rules.
  - **`api/deps.py`** — reusable dependencies: DB session, `get_current_user`
    (decodes JWT), `require_role(...)` — the server-side twin of the frontend
    `ProtectedRoute`.
  - **`api/v1/`** — versioned from day one so clients can evolve independently.
- **`core/`** — app-wide infrastructure.
  - `config.py` — a single `Settings` object read from env vars (the only place
    env vars are read).
  - `security.py` — JWT + password-hashing primitives.
  - `exceptions.py` — typed domain errors mapped to HTTP responses.
- **`db/`** — engine, session lifecycle, declarative base, Alembic migrations.
- **`models/`** — SQLAlchemy ORM classes; imported only by repositories (and
  Alembic).
- **`schemas/`** — Pydantic DTOs = the API contract. ORM models are never
  returned directly.
- **`repositories/`** — the only layer that talks to the database.
- **`services/`** — all business logic (state machines, assignment, duplicate
  detection, schedules, analytics). Depend on repositories, not on FastAPI.
- **`middleware/`** — request id, structured logging, error handling, CORS.
- **`utils/`** — pure, dependency-free helpers (direct ports of the frontend
  `utils/`).

### Dependency flow (one-directional)

```
api/routes  ──►  services  ──►  repositories  ──►  models  ──►  db (PostgreSQL)
     │              ▲
   schemas        core (config, security, exceptions)   utils (pure helpers)
```

Rules: routes → services → repositories → models/db, never skipping a layer.
Dependencies point inward; `core` and `utils` are leaf layers. Schemas (Pydantic)
and models (ORM) never mix — services translate between them, so the API contract
and DB schema evolve independently.

---

## Domain model (derived from the frontend)

Central aggregate is **Task / Assignment**, which links a Complaint *or* a Bulk
Pickup to the crew, vehicle, and equipment fulfilling it.

- **User** — `citizen` / `crew` / `admin` / `authority`; bcrypt-hashed password;
  JWT auth. `authority` is a fourth role for US-27 (Senior Authority performance
  reports); Health Officer (US-09) is treated as an `admin` capability rather than
  its own role. See `../SPRINT_PLAN.md` §15.2.
- **Ward** — first-class entity referenced by complaints, pickups, workers,
  vehicles, and schedules (instead of free-text strings).
- **Complaint** — `Pending → In Progress → Resolved / Cancelled`; geo coords,
  hazard classification, photo. Cancel only while `Pending`.
- **BulkPickup** — `Requested → Scheduled → Collected / Cancelled`. **Carries a
  computed `fee`.** An earlier version of this README said there was no fee; the
  frontend's `BulkPickupContext.calculateFee()` already implements load bands
  (₹150/300/600/1000) plus category surcharges and displays the result, so the
  API returns a fee to match working UI. Informational only — there is no payment
  processing. See `../SPRINT_PLAN.md` §15.1.
- **Task / Assignment** — links a Complaint/BulkPickup to Worker(s), Vehicle,
  and Equipment; owns its status and resolution data.
- **Worker / Vehicle / Equipment** — assignable resources with availability
  status; equipment tracks stock counts.
- **TransparencyFeedPost** — auto-generated when a task completes; carries
  before/after photos, applauds, and comments.
- **CollectionSchedule** — per-ward pickup timetable (static config for now).

### Open decisions (assumptions in effect, override anytime)

1. Ward is a first-class entity.
2. Auth = JWT access + refresh, bcrypt hashing; citizens self-register, crew and
   admins are provisioned by an admin.
3. Feed posts are auto-derived on complaint resolution.
4. Collection schedule stays static config for now.
5. Timestamps stored in UTC, ISO-8601 at the API boundary.
6. Status changes are recorded in a lightweight history/audit table.
7. List endpoints get pagination + filtering.
8. Duplicate detection is advisory (returns matches; does not block submit),
   using the same thresholds as the frontend (200 m / 0.6 / 0.35).

---

## Getting started

### 0. Install the two tools you need

Everything else is installed for you by `uv`.

**uv** — package manager and virtualenv manager. You do *not* need to install
Python separately; uv fetches the right version itself.

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Then **restart your shell** (the installer adds `~/.local/bin` to `PATH`) and check:

```bash
uv --version     # expect 0.12.x or newer
```

**Docker Desktop** (macOS/Windows) or **Docker Engine + compose plugin** (Linux) —
only used to run PostgreSQL. Verify with `docker compose version`.

> Don't want Docker? See [Running without Docker](#running-without-docker) below.

### 1. Clone and set up

```bash
git clone git@github.com:pankuzj/MAY2026-Team-028.git
cd MAY2026-Team-028/Backend

cp .env.example .env      # defaults work as-is for local development
uv sync --all-groups      # creates .venv/ and installs everything from uv.lock
```

`uv sync` is fast (a few seconds) and **reads `uv.lock`**, so you get byte-identical
versions to everyone else and to CI. It does not touch your system Python.

### 2. Start the database

```bash
docker compose up -d db       # PostgreSQL 16 on localhost:5432
docker compose ps             # wait until state shows "healthy"
```

Data persists in the `pgdata` volume across restarts. `docker compose down` stops
the container and keeps your data; `docker compose down -v` deletes it.

### 3. Apply migrations

```bash
uv run alembic upgrade head
```

Right now there are no revisions yet (migration 0001 is task S1-F08), so this is a
no-op that succeeds — it still confirms your `DATABASE_URL` is correct.

### 4. Run the API

```bash
uv run uvicorn app.main:app --reload
```

Then open:

| URL | What it is |
|---|---|
| <http://localhost:8000/docs> | **Swagger UI** — interactive, try any endpoint from the browser |
| <http://localhost:8000/redoc> | ReDoc, nicer for reading |
| <http://localhost:8000/openapi.json> | The spec FastAPI generates from the code |
| <http://localhost:8000/health/live> | Is the process up? |
| <http://localhost:8000/health/ready> | Is the process up **and** the database reachable? |

Confirm the whole chain works:

```bash
curl -i localhost:8000/health/ready
# HTTP/1.1 200 OK
# x-request-id: 4f2a9c1e8b0d3a67
# {"status":"ready","database":"ok"}
```

If that returns `503`, the app is fine and the **database** is not — check
`docker compose ps` and your `DATABASE_URL`.

### 5. Run the tests

```bash
uv run pytest                       # fast suite: SQLite in memory, ~1 second
uv run pytest -v                    # with each test name
uv run pytest --cov=app --cov-report=term-missing
uv run pytest tests/api/test_health.py::TestReadiness    # one class
```

Plain `uv run pytest` never needs PostgreSQL — it uses in-memory SQLite, so you can
run it on a plane. The integration suite is excluded by default and needs a real
database:

```bash
DATABASE_URL=postgresql+psycopg://smartsweep:smartsweep@localhost:5432/smartsweep_test \
  uv run pytest -m integration
```

### 6. Install the git hooks (once)

```bash
uv run pre-commit install
```

Now Ruff and Black run on every `git commit` and fix most issues automatically. This
is the same check CI runs, so it saves you a round trip through a red pipeline.

---

## Everyday commands

| I want to… | Command |
|---|---|
| Run the API with auto-reload | `uv run uvicorn app.main:app --reload` |
| Run the fast tests | `uv run pytest` |
| Run one test file | `uv run pytest tests/api/test_health.py -v` |
| See coverage gaps | `uv run pytest --cov=app --cov-report=term-missing` |
| Lint | `uv run ruff check .` |
| Lint and auto-fix | `uv run ruff check --fix .` |
| Format | `uv run black .` |
| Check formatting without changing files | `uv run black --check --diff .` |
| Add a dependency | `uv add <package>` (updates `pyproject.toml` **and** `uv.lock` — commit both) |
| Add a dev-only dependency | `uv add --dev <package>` |
| Remove a dependency | `uv remove <package>` |
| Create a migration | `uv run alembic revision --autogenerate -m "0002 add feedback"` |
| Apply migrations | `uv run alembic upgrade head` |
| Undo the last migration | `uv run alembic downgrade -1` |
| Which migration am I on? | `uv run alembic current` |
| Open a psql shell | `docker compose exec db psql -U smartsweep -d smartsweep` |
| Reset the database completely | `docker compose down -v && docker compose up -d db && uv run alembic upgrade head` |
| Run a one-off script in the venv | `uv run python scripts/whatever.py` |

**Always prefix with `uv run`.** It executes inside the project's `.venv` without
you having to activate anything. Never `pip install` into this project — that
bypasses `uv.lock` and your environment silently stops matching everyone else's.

---

## Running without Docker

If Docker will not install on your machine, you have two options.

**Option A — PostgreSQL installed natively.** Install PostgreSQL 16, then:

```bash
createuser -s smartsweep
createdb -O smartsweep smartsweep
psql -c "ALTER USER smartsweep WITH PASSWORD 'smartsweep';"
```

Your existing `DATABASE_URL` then works unchanged.

**Option B — SQLite, for writing services and utils only.** Put this in `.env`:

```
DATABASE_URL=sqlite:///./smartsweep_dev.db
```

Good enough for developing pure logic and running `uv run pytest`. **Not good
enough before you push:** SQLite does not enforce foreign keys by default, has no
real timestamp type, and cannot `ALTER` most columns. CI runs the integration suite
on real PostgreSQL, so code that only ever ran on SQLite can pass locally and fail
in the pipeline. Ask a teammate to run your branch against Postgres if you cannot.

---

## Running the whole stack in Docker

You do not need this for day-to-day work — it is slower to iterate on than
host-side uvicorn. Use it to check the image builds before the demo, or on a
machine with nothing but Docker.

```bash
cd Backend
cp .env.example .env
docker compose up --build        # db + api together
docker compose logs -f api       # follow the API logs
docker compose down
```

The API is on <http://localhost:8000> as before. Compose overrides `DATABASE_URL`
to point at the `db` service, because inside the container network `localhost`
means the container itself, not your machine.

---

## Frontend + backend together

Two terminals:

```bash
# terminal 1 — API on :8000
cd Backend && docker compose up -d db && uv run uvicorn app.main:app --reload

# terminal 2 — Vite dev server on :5173
cd Frontend && npm ci && npm run dev
```

`CORS_ORIGINS` in `.env` already allows `http://localhost:5173`. If the browser
console shows a CORS error, check that first — and note that a **500** from the API
also surfaces as a CORS error in the browser (Starlette's error middleware sits
outside the CORS layer). Read the real status from the uvicorn log rather than
chasing a CORS misconfiguration that isn't there.

---

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| `uv: command not found` | Installer added `~/.local/bin` to `PATH` — restart your shell. |
| `ModuleNotFoundError: No module named 'app'` | You ran `python` instead of `uv run python`, or you are not in `Backend/`. |
| `ModuleNotFoundError` from an alembic command | Same — run alembic from `Backend/`, via `uv run`. |
| `/health/ready` returns 503 | Database unreachable. `docker compose ps`, then check `DATABASE_URL`. |
| `connection refused` on port 5432 | The `db` container is not up yet. `docker compose up -d db` and wait for `healthy`. |
| `password authentication failed` | Your `.env` credentials do not match `docker-compose.yml`. Or you have another PostgreSQL already using 5432 — `docker compose down -v` and recreate. |
| CI fails at "Install dependencies (lockfile must be current)" | Someone edited `pyproject.toml` without committing `uv.lock`. Run `uv sync --all-groups` and commit the lockfile. |
| CI fails on `black --check` | Run `uv run black .` and commit. Install the pre-commit hooks so this stops happening. |
| Ruff flags `B008` on `Depends(...)` | Should not happen — `pyproject.toml` allowlists FastAPI's injection calls. If it does, you are running Ruff from outside `Backend/`. |
| `alembic` autogenerates a surprise `drop_table` | Your model module is missing from `app/db/base_models.py`. Alembic cannot see a model it never imported. |
| Tests pass locally, integration fails in CI | SQLite-vs-PostgreSQL difference — foreign keys, timezone-aware timestamps, or case sensitivity. |
| Every log line shows `[-]` instead of a request id | You are looking at a startup line, logged before any request. |

---

## Development workflow

### Git

- Branch names **lead with the task ID** so the board and the branch line up:
  `feature/S1-A03-complaint-routes`, `fix/S1-A06-task-status-409`.
- Open a PR, get one approving review, then **squash-merge**. The PR template
  (`.github/pull_request_template.md`) is filled in automatically — complete it.
- [Conventional Commits](https://www.conventionalcommits.org): `feat:`, `fix:`,
  `chore:`, `docs:`, `test:`. Reference stories in the body: `Implements US-01, US-04.`
- **`main` is not protected yet.** An earlier version of this README claimed it
  was; the GitHub API reports otherwise, so anyone can currently push or
  force-push to it. Fixing that is task S1-C07 — the command is in
  `../SPRINT_PLAN.md` section 13.1. Until it lands, protection is a convention we
  keep by hand, not a rule the platform enforces.

### Testing

Three suites, three purposes:

| Directory | Tests what | Database | In default `pytest` run? |
|---|---|---|---|
| `tests/unit/` | services and pure utils, DB faked | none | yes |
| `tests/api/` | full request cycle via `TestClient` | SQLite in memory | yes |
| `tests/integration/` | repositories and DB behaviour | real PostgreSQL | **no** — `-m integration` |

`tests/integration` is excluded from the default run by `addopts` in
`pyproject.toml`, so the fast suite stays fast and needs no database. CI runs both.

Shared fixtures live in `tests/conftest.py`: `client`, `db`, `app`, plus
`citizen_token` / `crew_token` / `admin_token` and `citizen_client` /
`crew_client` / `admin_client`. **The names are final and the bodies are stubs** —
write tests against them now; they start passing when auth and the models land
(task S1-F11).

### Migrations

- Autogenerate, then **review every migration by hand** before committing.
  Alembic is reliable for tables and columns and unreliable for renames, type
  changes, and constraints — a rename comes out as drop + add, which deletes data.
- **Add every new model module to `app/db/base_models.py`.** Alembic diffs
  `Base.metadata` against the live database, and a model whose module was never
  imported looks like a table that should be dropped.
- Never edit a migration that has been applied anywhere but your own machine —
  roll forward with a new revision. See `app/db/migrations/README`.

### Docker

- `docker compose up -d db` — just PostgreSQL. **This is what you want day to day.**
- `docker compose up --build` — `api` + `db` together, for verifying the image.
- The `Dockerfile` is a two-stage uv build: dependencies resolved in a builder
  stage, only the finished virtualenv copied into a slim runtime that runs as a
  non-root user.

### Quality gates

- `uv run pre-commit install` once — then Ruff + Black run on every commit.
- CI (`.github/workflows/backend-ci.yml`) runs, in fail-fast order: lockfile
  freshness → Ruff → Black → fast tests with a **70% coverage floor** → migrations
  up **and back down** → integration tests on real PostgreSQL.
- Two more workflows: `frontend-ci.yml` (oxlint + Vite build) and
  `openapi-lint.yml` (Spectral against `docs/**/openapi.yaml`).
- Required status checks for `main`, once branch protection is enabled:
  `quality`, `frontend`, `openapi-lint`. These are **job names** — renaming a job
  silently disables its protection.

---

## Status

The foundation is done and verified: `uv sync` installs, the app boots,
`/health/*` responds, Alembic connects, 43 tests pass, coverage is 87%, and Ruff
and Black are clean.

| Layer | State |
|---|---|
| Dependencies and `uv.lock` | Done — 57 packages pinned |
| `core/config.py`, `core/logging.py` | Done |
| `core/exceptions.py` and the error envelope | Done |
| `schemas/common.py` (error and pagination envelopes) | Done |
| `db/base.py`, `db/base_models.py`, `db/session.py` | Done |
| `middleware/request_context.py` | Done |
| `main.py` app factory and health probes | Done |
| Alembic environment and template | Wired, but no revisions exist yet (S1-F08) |
| CI: backend, frontend, OpenAPI lint | Enabled and passing |
| Dockerfile and compose `api` service | Written but never built — see the note below |
| `core/security.py` (bcrypt and JWT) | Not started — S1-F04, Sagnik |
| `api/deps.py` auth dependencies | Signatures published, bodies stubbed — S1-A08, Sagnik |
| `tests/conftest.py` token and data fixtures | Names published, bodies stubbed — S1-F11, Jatin |
| Models, schemas, repositories, services, routes | Not started — see `../SPRINT_PLAN.md` section 9 |

Two things are written but unproven, so please do not assume they work. The Docker
image has never been built, because there was no Docker on the machine this was
written on — someone should run `docker compose up --build` before the demo.
And `alembic revision --autogenerate` has never been run, because there are no
models to diff yet; whoever writes migration 0001 will be the first to exercise it.

Every remaining `# TODO` names its task ID and owner. The reasoning behind each
setup decision is in `../docs/DEV_LOG.md`.
