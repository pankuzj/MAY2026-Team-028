# SmartSweep — Backend

Backend for **SmartSweep**, a civic waste-management platform for reporting and
tracking garbage/waste-collection issues across three roles: **Citizen**,
**Cleanup Crew**, and **Ward Supervisor / Admin**.

This document is the shared blueprint for the team. It describes the target
architecture, what each folder is for, how the layers depend on one another,
and how we work (Git, tests, migrations, Docker, CI). **This is the scaffold
phase** — the folder tree and tooling are in place, but models, endpoints,
migrations, and business logic are intentionally *not* implemented yet. Every
placeholder module carries a `# TODO` describing what belongs there.

> The API contract is largely pre-negotiated by the existing React frontend
> (`../Frontend`): its context mutators were written `async` on purpose so that
> swapping their bodies for `fetch()` calls to this backend won't require
> touching UI components.

---

## Tech stack

| Concern | Choice |
|---|---|
| Language | Python 3.13+ |
| Web framework | FastAPI |
| ORM | SQLAlchemy 2.0 |
| Database | PostgreSQL |
| Migrations | Alembic |
| Validation / DTOs | Pydantic v2 |
| Testing | Pytest |
| Packaging / venv | uv |
| Containers | Docker + Docker Compose |
| Lint / format | Ruff + Black |
| Git hooks | pre-commit |
| CI | GitHub Actions |

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

- **User** — `citizen` / `crew` / `admin`; hashed password; JWT auth.
- **Ward** — first-class entity referenced by complaints, pickups, workers,
  vehicles, and schedules (instead of free-text strings).
- **Complaint** — `Pending → In Progress → Resolved / Cancelled`; geo coords,
  hazard classification, photo. Cancel only while `Pending`.
- **BulkPickup** — `Requested → Scheduled → Collected / Cancelled`. (No fee /
  payment — service is municipality-run.)
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

## Development workflow

### Getting started (once dependencies are pinned)

```bash
cd Backend
cp .env.example .env          # fill in local values
uv sync                       # create venv + install deps
docker compose up -d db       # start PostgreSQL
uv run alembic upgrade head   # apply migrations
uv run uvicorn app.main:app --reload
```

### Git

- `main` is protected and always deployable.
- Work on short-lived branches (`feature/*`, `fix/*`), open a PR, get one review,
  then squash-merge. Use Conventional Commit messages
  (`feat:`, `fix:`, `chore:`, `docs:`, `test:`).

### Testing

- `tests/unit` — services and utils with the DB faked (where the logic lives;
  aim for high coverage here).
- `tests/integration` — repositories against a real Postgres test DB.
- `tests/api` — full request cycle via `TestClient`.
- Run: `uv run pytest` (with `--cov=app` for coverage).

### Migrations

- Autogenerate with Alembic, but **review every migration by hand** before
  committing. Never edit an applied migration — always roll forward.

### Docker

- `docker compose up` brings up `api` + `postgres` for local dev.
- The `Dockerfile` builds the production image (multi-stage, via uv).

### Quality gates

- `pre-commit install` runs Ruff + Black + basic hygiene on every commit.
- CI (`.github/workflows/backend-ci.yml`) re-runs lint, format check,
  migrations, and tests on every PR; merges are blocked on failure.

---

## Status

Scaffold only. Package tree and tooling are in place; models, schemas,
repositories, services, endpoints, migrations, and auth are **not implemented
yet** — see the `# TODO` markers in each module.
