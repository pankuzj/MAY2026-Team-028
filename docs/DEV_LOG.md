# SmartSweep — Development Log

A running record of **what was built, what was decided, and why**, plus the
background needed to understand the decisions. Newest entry first.

This is not a changelog (git does that) and not documentation (the READMEs do
that). It captures the reasoning that would otherwise be lost — the "why is it
like this" questions that come up in review, in the demo, and six months later.

**How to use it:** add an entry when you make a decision someone could reasonably
have made differently. Give it an ID (`D-xx`), state the alternatives you rejected,
and say what would make you change your mind. Reference the ID from code comments
so the code points back here.

---

# 2026-07-30 — Environment, tooling, CI, and application skeleton

**Owner:** Pankaj · **Tasks:** S1-F01, F02, F03, F05, F06, F07, F09, F10, M08 ·
partial support for F04, F08, F11, A08

## What this session delivered

The `Backend/` folder went from 27 files of docstrings and `# TODO` markers — zero
executable lines — to a running application with green CI.

| Task | Deliverable | State |
|---|---|---|
| S1-F01 | Deps pinned, `uv.lock` generated (57 packages) | done |
| S1-F02 | `app/core/config.py` — 25 settings, validated | done |
| S1-F03 | `app/db/base.py`, `base_models.py`, `session.py` | done |
| S1-F05 | `app/core/exceptions.py` — 8 typed errors + 4 handlers | done |
| S1-F06 | `app/middleware/request_context.py` — request id + access log | done |
| S1-F07 | `app/main.py` — app factory, lifespan, CORS, health routes | done |
| S1-F09 | Two-stage `Dockerfile`, compose `api` service | written, **not built** |
| S1-F10 | `backend-ci.yml` enabled, `frontend-ci.yml` and `openapi-lint.yml` added | done |
| S1-M08 | `app/schemas/common.py` — error + pagination envelopes | done |
| — | `app/core/logging.py`, `app/api/health.py`, `app/api/v1/router.py` | done |
| — | Alembic `env.py`, `script.py.mako`, `alembic.ini`, migrations README | done |
| — | `.spectral.yaml`, PR template, `CODEOWNERS` scaffold | done |
| — | 43 tests across 3 files, 87% coverage | done |
| S1-F04 | `app/core/security.py` | **untouched — Sagnik** |
| S1-A08 | `app/api/deps.py` | **signatures published, bodies stubbed — Sagnik** |
| S1-F11 | `tests/conftest.py` | **fixture names published, data bodies stubbed — Jatin** |
| S1-F08 | Migration 0001 | **environment wired, no revisions — Nitin** |

### Verified, not assumed

```
uv sync --all-groups --locked   -> 57 packages, lockfile current
uv run ruff check .             -> All checks passed
uv run black --check .          -> 34 files unchanged
uv run pytest                   -> 43 passed in 0.29s
uv run pytest --cov=app         -> 87% (gate set at 70%)
uv run alembic current/upgrade/history -> connects, no-ops cleanly
python -c "from app.main import app"   -> builds, 6 routes
```

### Explicitly NOT verified — do not assume these work

1. **The Docker image has never been built.** There is no Docker on the machine
   this was authored on. The `Dockerfile` and compose file are written carefully
   but unproven. **Someone with Docker must run `docker compose up --build` before
   the demo** and report back here. Most likely failure points: the
   `ghcr.io/astral-sh/uv:0.12.0` tag, and the `HEALTHCHECK` (it uses `urllib` from
   the venv's Python, which should be on `PATH`, but that is untested).
2. **`alembic revision --autogenerate` was not run.** `current`, `upgrade head`,
   `history`, and `downgrade base` all work, but autogenerate has never produced a
   file here because there are no models yet. Nitin will be first to exercise it
   (S1-F08); if `target_metadata` is wrong, that is where it surfaces.
3. **No CI run has happened.** The workflows are syntactically valid YAML and the
   commands they run were all verified locally, but GitHub Actions has not executed
   them. Expect one or two rounds of fixes on the first PR.
4. **The integration suite has never run against real PostgreSQL** locally, for the
   same reason as (1). It will first run in CI.

---

## Decisions

### D-01 · Python 3.12, not 3.13

`pyproject.toml` required `>=3.13`. Nobody's machine has 3.13 — the dev box here
runs 3.12.3 — and nothing in the stack needs it.

Rejected: keeping 3.13 and having `uv` download it. That works, but it means the
whole team develops on a Python version none of them installed deliberately, and
CI would test a version nobody runs locally. That asymmetry produces bugs that
reproduce only in CI, which are the most expensive kind to debug.

**Changed:** `requires-python = ">=3.12"`, Ruff/Black `target-version = "py312"`,
CI and both Docker stages on `3.12`.

*Change this if* a dependency starts requiring 3.13.

> **Teaching note — why a lower bound and no upper bound.** For a *library*, an
> upper bound (`>=3.12,<3.14`) protects users from a release you have not tested.
> For an *application* like this one, an upper bound only stops you upgrading. The
> lockfile already guarantees reproducibility, so the version range just needs to
> express the true minimum.

### D-02 · Comma-separated string for `CORS_ORIGINS`, not `list[str]`

The obvious typing is `cors_origins: list[str]`. It breaks. pydantic-settings tries
to **JSON-decode** any complex type read from the environment, so
`CORS_ORIGINS=http://localhost:5173` raises a parse error — it is not valid JSON.
The workaround people reach for is `CORS_ORIGINS=["http://localhost:5173"]` in
`.env`, which is ugly and easy to get wrong with quoting in a shell.

**Chosen:** declare it a `str`, expose a `cors_origin_list` property that splits on
commas and strips blanks. Ordinary `.env` syntax, one place to change, tested in
`tests/unit/test_config.py::TestCorsParsing` (five cases including trailing commas
and stray whitespace).

Rejected: pydantic-settings' `NoDecode` annotation. It works on 2.7+, but it is a
subtle annotation whose absence silently reintroduces the bug.

### D-03 · Settings validate at import, and refuse to start on a weak prod secret

`Settings` has a `model_validator` that raises if `ENV=prod` and `JWT_SECRET_KEY`
is still `change-me` (or `secret`, or empty).

A weak signing key means anyone can mint an admin token — the entire RBAC layer
becomes decorative. The failure is silent: the app works perfectly, right up until
someone notices. Crashing at startup converts an invisible security hole into an
obvious, immediate, unmissable error. Local development is unaffected because the
check only fires when `ENV=prod`.

> **Teaching note — fail fast.** Prefer errors at the earliest possible moment:
> import time over first request, first request over "when this code path happens
> to run". The cost of a startup crash is minutes. The cost of a misconfiguration
> discovered in production is unbounded.

### D-04 · PyJWT + bcrypt, not python-jose + passlib

The blueprint named `python-jose[cryptography]` and `passlib[bcrypt]`.

- `passlib` 1.7.4 is unmaintained (last release 2020) and **crashes on
  `bcrypt>=4.1`** — it reads `bcrypt.__about__.__version__`, which was removed.
  Pinning `bcrypt<4.1` to work around it means pinning to a version with known
  fixes missing.
- `python-jose` has open CVEs and is barely maintained.

`PyJWT` is what FastAPI's own documentation uses, and `bcrypt`'s API is two
functions (`hashpw`, `checkpw`). Identical contract, materially fewer problems.

**Impact on Sagnik (S1-F04):** write `core/security.py` against `jwt.encode` /
`jwt.decode` and `bcrypt.hashpw` / `bcrypt.checkpw`. Note bcrypt takes and returns
`bytes`, so encode/decode at the boundary, and it silently truncates input at 72
bytes — validate password length in the schema rather than letting a long password
be quietly shortened.

### D-05 · One error envelope, defined once, enforced by four handlers

Every non-2xx response, from any source, has this shape:

```json
{"error": {"code": "NOT_FOUND", "message": "...", "details": [], "request_id": "..."}}
```

Four handlers guarantee it: our `AppError`, Starlette's `HTTPException` (framework
404s and 405s), Pydantic's `RequestValidationError` (422), and a catch-all for
`Exception` (500).

The third and fourth are the ones people forget. Without the `HTTPException`
handler, a request to a wrong URL returns Starlette's `{"detail": "Not Found"}` and
the frontend needs a second error-parsing branch for errors our code never
produced. `tests/api/test_health.py::TestErrorEnvelope` pins all of this.

`code` is stable and machine-readable; `message` is human-facing and can be
reworded freely. That split is what lets the frontend switch on `code` without
breaking every time someone improves the wording.

> **Teaching note — 401 vs 403.** Keep them distinct. 401 means "I do not know who
> you are" and the client should redirect to login. 403 means "I know who you are
> and you may not do this" and the client should say so. Collapsing them makes
> correct client behaviour impossible.

### D-06 · Services raise domain exceptions; only handlers know about HTTP

`app/services/` and `app/repositories/` must never `import fastapi`. A service
signals a missing row by raising `NotFoundError`, not by returning a 404.

Three payoffs: the same service can back an HTTP route, a CLI command, or a seed
script; every error response is identically shaped because exactly one function
builds it; and each layer is testable at its own level —
`pytest.raises(InvalidStateTransitionError)` on the service, `assert
response.status_code == 409` on the route.

`InvalidStateTransitionError` subclasses `ConflictError` (both 409) but carries its
own `code`, so the client can tell "you cannot do that *yet*" from a generic
conflict. That distinction matters for the complaint and task status machines,
where the UI should explain which transitions *are* legal.

### D-07 · Request id in a ContextVar, not a function parameter

Every request gets a 16-hex-char id (or reuses an inbound `X-Request-ID`),
published to a `ContextVar` that a logging filter reads. Every log line during that
request carries it; it goes back as a response header and into every error body.

Threading a `request_id` argument through route → service → repository would
pollute every signature in the codebase for a cross-cutting concern. Under asyncio
each task gets its own ContextVar copy, so concurrent requests cannot see each
other's id.

**Reusing an inbound header** is what lets one id span the frontend and the
backend: the browser generates it, the API logs it, the user reads it off an error
toast, and we grep for it. That turns "submitting a complaint failed" from a guess
into a lookup.

Ordering subtlety, worth knowing: the middleware resets the ContextVar in a
`finally`, and both log calls happen *before* that inside the `try`. An earlier
draft reset it first and every access-log line printed `[-]`.

### D-08 · SQLite for the fast suite, PostgreSQL only for integration

`tests/unit` and `tests/api` run on in-memory SQLite; `tests/integration` needs
real PostgreSQL and is **excluded from the default `pytest` run** via
`addopts = "... -m 'not integration'"`.

The fast suite runs in 0.29 seconds and needs no database, so nobody has an excuse
not to run it before pushing. CI runs both, in separate steps with different
`DATABASE_URL`s.

Three traps this arrangement contains, all handled:

1. **`conftest.py` sets `DATABASE_URL` before importing anything from `app`.**
   `app.core.config` builds its Settings at import time and `app.db.session` builds
   the engine from it at import time. By the time a fixture body runs it is far too
   late — the engine would already point at the developer's real database, and
   `create_all`/`drop_all` would wipe local dev data. Hence the env block at the
   very top of the file, before the imports, with `# noqa: E402` on them.
2. **`setdefault`, not assignment**, so CI can override with a PostgreSQL URL.
3. **`tests/integration/test_database.py` asserts it is not on SQLite.** Without
   that, forgetting `DATABASE_URL` makes the integration suite silently pass on
   SQLite, reporting green while testing nothing it exists to test.

SQLite and PostgreSQL genuinely disagree about things we depend on: foreign-key
enforcement (off by default in SQLite), timezone-aware timestamps, case-sensitive
comparison, and `ALTER TABLE`. Hence `render_as_batch=True` in Alembic and the
integration suite as a tripwire.

> **Teaching note — the rollback fixture.** The `db` fixture opens a connection,
> begins a transaction, binds the session to it, and rolls back at teardown.
> Everything a test wrote is discarded, *even if the code under test called
> `commit()`* — that commit ends only the inner transaction, not the outer one the
> fixture owns. The alternative, dropping and recreating the schema per test, is
> also correct and roughly two orders of magnitude slower.

### D-09 · `db/base.py` and `db/base_models.py` are separate files

`base.py` defines `Base` and `TimestampMixin`. `base_models.py` imports every model
module and is what Alembic points at.

They cannot be one file: models import `Base` from `base`, so `base` importing
models is a circular import.

Why `base_models.py` needs to exist at all: SQLAlchemy only knows a table exists
once its module has been imported. Alembic diffs `Base.metadata` against the live
database, so **a model whose module was never imported looks like a table that
should be dropped.** Autogenerate will cheerfully write `op.drop_table('complaints')`.
This is the single most common Alembic surprise, and the fix is always "add the
import". Both `base_models.py` and `app/db/migrations/README` say so.

### D-10 · Naming convention on `MetaData`

`Base.metadata` carries an explicit `naming_convention` for indexes, unique
constraints, checks, foreign keys, and primary keys.

Without it the database auto-names constraints, **differently on PostgreSQL and
SQLite**. Alembic then emits `op.drop_constraint(None, ...)`, which fails on
downgrade. Setting the convention up front means every constraint has a predictable
name that a hand-written migration can reference.

This has to be decided before migration 0001. Changing it later means every
existing constraint has the old name and every new one the new name.

### D-11 · Database URL lives in `env.py`, not `alembic.ini`

Alembic's generated template puts `sqlalchemy.url` in `alembic.ini`. Ours does not
have that key at all; `env.py` reads `settings.database_url` instead.

Two reasons: credentials in `alembic.ini` would be committed to git, and a
hard-coded URL means no way to target a different database per environment. Reading
from the same `Settings` the app uses also makes it impossible for `alembic upgrade
head` and the running application to disagree about which database they mean.

`prepend_sys_path = .` is required for this — the alembic console script does not
put the working directory on `sys.path`, and this project is not pip-installed into
the venv (no `[build-system]`, so uv treats it as a virtual project). Without that
line every alembic command fails with `ModuleNotFoundError: No module named 'app'`.

### D-12 · `-m 'not integration'` in `addopts`, and why CI still works

Command-line `-m` overrides the one in `addopts` (last occurrence of an option
wins, and addopts are prepended). So `uv run pytest` gets the fast suite and CI's
`uv run pytest -m integration` gets the other one.

Practical detail worth knowing: **`pytest` exits with code 5 when it collects zero
tests**, which fails a CI job. That is why `tests/integration/test_database.py`
exists rather than an empty directory, and part of why the health smoke tests were
written before any real endpoint — until an endpoint lands, they are what makes
"CI is green" a statement about anything.

### D-13 · B008 allowlisted for FastAPI's `Depends`

Ruff's bugbear B008 forbids function calls in argument defaults. It is correct in
general — a mutable default evaluated once at import is a classic Python bug — and
wrong for FastAPI, where `db: Session = Depends(get_db)` *is* the dependency
injection syntax and is evaluated per request.

It fired three times on `api/deps.py`. The alternatives were a `# noqa: B008` on
every route parameter in the project (hundreds of lines by the end of Sprint 2) or
one allowlist entry. Chose the allowlist:
`[tool.ruff.lint.flake8-bugbear] extend-immutable-calls` covering `Depends`,
`Query`, `Path`, `Body`, `Header`, `File`, `Form`, `Cookie`, `Security`.

### D-14 · Health probes are unversioned, and split live/ready

`/health/live` and `/health/ready`, not `/api/v1/health`. These are operational
endpoints, not product API. Versioning them would imply a future `/api/v2/health`,
and Docker healthchecks and CI wait-loops need one URL that never moves.

The split is the standard one and it matters: **live** touches nothing external, so
a failure means "restart the container". **ready** checks the database, so a
failure means "the dependency is down, restarting will not help". Collapse them and
a two-second database blip triggers a restart loop of a perfectly healthy app.

`/health/ready` returns 503 with the standard error envelope when the database is
unreachable — so even the failure path is consistent with everything else.

### D-15 · `create_app()` factory, plus a module-level `app`

`create_app()` builds and returns a configured app; `app = create_app()` at module
bottom exists because `uvicorn app.main:app` needs an importable target.

Tests build a fresh app per test (`conftest.py`'s `app` fixture), so a test that
overrides a dependency or mutates app state cannot leak into the next one. With a
single module-level app, `dependency_overrides` accumulate across tests and produce
failures that depend on test execution order.

`upload_dir.mkdir()` is in the `lifespan` handler rather than at import time, so
importing `app.main` has no filesystem side effects — which matters because
Alembic, pytest collection, and `--help` all import this module.

### D-16 · CORS added last; and a limitation to know about

Middleware added *last* sits *outermost*. CORS goes last so it wraps everything
below and attaches headers to the 4xx envelopes our handlers produce.

**Known limitation, documented in `main.py` and the README:** Starlette's
`ServerErrorMiddleware` sits outside *all* user middleware, so a 500 from the
catch-all handler is returned **without CORS headers**. The browser surfaces it as
a CORS error rather than as the 500 it is.

This wastes an afternoon if you do not know it. When the console says CORS and you
did not change CORS config, read the server log — the request id is in both places.

`expose_headers=["X-Request-ID"]` is also required, or the browser hides the header
from JavaScript and the frontend cannot put the id in an error toast.

### D-17 · CI gates in fail-fast order, with a lockfile check first

`uv sync --all-groups --locked` → Ruff → Black → fast tests (70% floor) →
`alembic upgrade head` → `downgrade base && upgrade head` → integration tests.

- **`--locked` first.** It fails if `uv.lock` disagrees with `pyproject.toml`
  instead of silently re-resolving. That catches "someone edited `pyproject.toml`
  and forgot to commit the lockfile", which otherwise means CI tested different
  dependency versions than any human ran.
- **Cheap checks before expensive ones.** A formatting error is reported in ~20
  seconds, not after a four-minute test run.
- **Coverage floor 70%,** the plan's Sprint 2 target. Currently at 87%, so it
  passes with headroom now and the number never has to be argued about later.
- **Downgrade then upgrade.** Verifies migrations are reversible. This is the only
  automated check that a bad deploy can be rolled back, and it costs seconds.

Job names `quality`, `frontend`, `openapi-lint` are the required status checks in
the branch-protection rule. **GitHub matches contexts by name — renaming a job
silently disables its protection.**

### D-18 · `x-user-story` enforced by a custom Spectral rule

The rubric requires user-story → endpoint mapping. A table in a document goes stale
the moment someone adds an endpoint. `.spectral.yaml` has a custom rule requiring
every operation to carry `x-user-story`, at severity `error`.

That makes the trace machine-checkable: an endpoint without its US ids fails CI.
`operation-description`, `operation-summary`, and `operation-operationId` are also
promoted to `error` because those are the exact things the rubric marks.

`openapi-lint.yml` also guards against a subtler failure: with no spec files the
glob matches nothing and Spectral exits 0, so the job would report green while
linting nothing. It checks for the files first and emits a warning annotation
instead.

### D-19 · Docker: two stages, non-root, deps before source

- **Two stages** — uv, the build toolchain, and the package cache stay in the
  builder. The runtime image gets only the finished virtualenv: smaller, and
  without tools an attacker could use post-compromise.
- **`--frozen`, not `--locked`** — installs the lockfile exactly and never
  re-resolves. A container that resolved different versions than CI tested is
  "works on my machine", one layer down.
- **`--no-dev`** — pytest, ruff, and black have no business in a runtime image.
- **Non-root user** (uid 1001) — a compromised process cannot write outside what
  it owns or install packages. `uploads/` is created and chowned at build time
  because the non-root user cannot `mkdir` later.
- **`pyproject.toml` + `uv.lock` copied and installed *before* `app/`** — editing a
  Python file then rebuilds one cheap layer instead of reinstalling 57 packages.
- **`HEALTHCHECK` hits `/health/ready`**, so "healthy" means "can reach the
  database", not merely "the process started".

Compose overrides `DATABASE_URL` to `db:5432` for the `api` service, because inside
the container network `localhost` is the container itself. A `.env` written for
host-side development points at `localhost:5432` and would otherwise fail
confusingly.

### D-20 · Publish signatures before bodies for the two risky handoffs

The plan identifies `api/deps.py` (S1-A08) and `tests/conftest.py` (S1-F11) as the
two highest-risk handoffs — four people are blocked on each. Both are now published
**signature-first**:

- `deps.py` — `get_db` fully works; `get_current_user` and `require_role(*roles)`
  exist with final signatures and docstrings, raising `NotImplementedError` until
  `core/security.py` lands. The `require_role` closure is already correct and
  starts working the moment `get_current_user` returns a real user.
- `conftest.py` — `client`, `db`, `app`, `test_settings`, `db_engine` all work.
  `seed_ward`, `seed_complaint`, `citizen_token`, `crew_token`, `admin_token`,
  `citizen_client`, `crew_client`, `admin_client` exist and call `pytest.skip` with
  a message naming the blocking task.

Route authors and test authors can write **final** code today — correct imports,
correct type hints, correct fixture names. When Sagnik and Jatin fill the bodies, no
caller changes. `pytest.skip` rather than `fail` is deliberate: dependent tests
report as skipped with a reason, not as noise in a red suite.

### D-21 · Schedule reality — the foundation landed on day 5, not day 1

Recorded plainly because the plan's central risk was exactly this. `SPRINT_PLAN.md`
§8 sets a "Day-1 rule": S1-F01→F02→F03→F04→F05→F08→F11 merged within the first 24
hours, because everything else is blocked on them. Sprint 1 opened Jul 23. This
work landed **2026-07-30**, five days in, and F04/F08/F11 are still open.

Two consequences to plan around rather than discover:

1. The remaining Sprint 1 scope (21 endpoints) has ~3 days, not 11. The plan's
   mid-sprint checkpoint (§13.6, Jul 31) says: if fewer than 14 of 21 endpoints are
   merged, cut to Option C — Auth + Complaint CRUD + duplicate detection, 13
   endpoints — rather than ship 21 half-finished ones. That checkpoint is now
   essentially immediate.
2. The signature-first handoffs (D-20) exist specifically to buy some of this time
   back: nobody has to wait on `deps.py` or `conftest.py` bodies to write final
   code.

Commit dates in this repository are true authoring dates. If the timeline is
discussed in the retro, this entry is the record.

## Known issues and follow-ups

| # | Issue | Owner | Notes |
|---|---|---|---|
| 1 | Docker image never built | anyone with Docker | `docker compose up --build`, report back here |
| 2 | `alembic revision --autogenerate` never exercised | Nitin (S1-F08) | first real use is migration 0001 |
| 3 | CI has never run | Pankaj | expect fixes on the first PR |
| 4 | `main` is unprotected | Pankaj (S1-C07) | command in SPRINT_PLAN §13.1; enable checks only after each job has run once |
| 5 | `CODEOWNERS` fully commented out | Pankaj | needs real GitHub handles; GitHub ignores unknown users silently |
| 6 | `conftest.db_engine` calls `create_all` even against PostgreSQL | Jatin (S1-F11) | harmless now (no models). Once models exist, integration tests should use the Alembic-built schema instead — otherwise two sources of truth for DDL |
| 7 | `Frontend/README.md` says React 18; `package.json` says 19.2.7 | Jatin | plan §13.7 |
| 8 | Root `package-lock.json` (95 bytes, stray) | Pankaj | deleted in this session |
| 9 | No frontend test runner at all | Jatin | out of Sprint 1 scope; flag if the rubric wants it |

## For the team — what to do next

**Sagnik — you are the critical path.** `core/security.py` (S1-F04) unblocks
`deps.py`, which unblocks all 20 protected endpoints. Use `pyjwt` and `bcrypt`
directly (D-04). The signatures in `api/deps.py` are already published, so filling
the bodies changes no caller.

**Nitin — migration 0001 (S1-F08).** Add each model module to
`app/db/base_models.py` *before* autogenerating, or Alembic will offer to drop
tables it cannot see (D-09). Review the generated file by hand; the checklist is in
`script.py.mako`'s docstring.

**Jatin — `conftest.py` data fixtures (S1-F11).** The names are published and
skipping with a reason. Also see follow-up 6 above.

**Vishal — models and complaint routes.** `Base` and `TimestampMixin` are in
`app/db/base.py`. Raise the typed errors from `core/exceptions.py`; do not build
HTTP responses in a service (D-06).

**Everyone, once:**

```bash
cd Backend && uv sync --all-groups && uv run pre-commit install
```

Read `Backend/README.md` → *Getting started*. If `uv run pytest` is not green on a
fresh clone, say so immediately — that is a foundation bug, not your bug.
