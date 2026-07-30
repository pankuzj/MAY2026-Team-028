# SmartSweep — Sprint 1 & Sprint 2 Master Plan

**Team:** ScrumMisfits (Team-028) · **Project:** SmartSweep — Civic Waste Management Platform
**Jira epics:** SE-may-029 (Sprint 1) · SE-may-030 (Sprint 2) · SE-may-031 (Milestone 5)
**Plan generated:** 2026-07-28

---

## TABLE OF CONTENTS

1. [Schedule reality check — read this first](#1-schedule-reality-check)
2. [Where the codebase actually stands today](#2-where-the-codebase-actually-stands-today)
3. [Master user story list (33 stories)](#3-master-user-story-list)
4. [User story → feature → API endpoint mapping](#4-user-story--feature--api-endpoint-mapping)
5. [APIs we build vs APIs we integrate](#5-apis-we-build-vs-apis-we-integrate)
6. [Sprint 1 scope](#6-sprint-1-scope)
7. [Sprint 2 scope](#7-sprint-2-scope)
8. [Dependency graph & ordering rules](#8-dependency-graph--ordering-rules)
9. [Sprint 1 — full task list with owners](#9-sprint-1--full-task-list-with-owners)
10. [Sprint 2 — full task list with owners](#10-sprint-2--full-task-list-with-owners)
11. [Workload balance check](#11-workload-balance-check)
12. [Deliverables checklist (rubric-mapped)](#12-deliverables-checklist)
13. [PM setup — boards, workflows, branch protection, CI](#13-pm-setup)
14. [Tooling recommendations](#14-tooling-recommendations)
15. [Assumptions & open decisions](#15-assumptions--open-decisions)

---

## 1. SCHEDULE REALITY CHECK

Your Milestone 2 report and Jira CSVs set this schedule:

| Phase | Dates | Status as of 2026-07-28 |
|---|---|---|
| Milestone 2 — Design + Frontend | Jul 1 – Jul 22 | **Done** — frontend is real and working |
| Milestone 3 / Sprint 1 — API Development | Jul 23 – Aug 2 | **At risk** |
| Milestone 4 / Sprint 2 — Integration & Testing | Aug 3 – Aug 12 | Not started |
| Milestone 5 — Final Submission | Aug 13 – Aug 23 | Not started |

**The problem:** Sprint 1 is 6 of 11 days elapsed. Your CSV had 9 backend tasks due Jul 25–29.
The `Backend/` folder currently contains **zero lines of executable code** — 27 Python files that
are all docstring + `# TODO` + `__all__ = []`. `pyproject.toml` has every dependency commented
out, so `uv sync` installs nothing. Alembic is a 2-line placeholder. CI has every real step
commented out.

**What this means:** ~100% of Sprint 1 engineering work remains, with 5 calendar days left.

**Recommended response — pick one, decide at the next standup:**

- **Option A (recommended): Compress, don't cut.** Treat Jul 28–Aug 2 as a hard push. Sprint 1
  scope below is already trimmed to the critical path (21 endpoints). Achievable with 5 people
  working in parallel *if* the foundation tasks (S1-F01…F08) land within the first 24 hours,
  because everything else is blocked on them.
- **Option B: Re-baseline the sprint.** Shift Sprint 1 to Jul 28 – Aug 5 and Sprint 2 to
  Aug 6 – Aug 14, compressing Milestone 5 to Aug 15–23. Costs you slack at the end.
- **Option C: Descope Sprint 1** to Auth + Complaint CRUD + duplicate detection only (13
  endpoints), and push all task-assignment work to Sprint 2. Safest for quality, but Sprint 2
  becomes very heavy.

This plan is written for **Option A**. If you choose B or C, the task tables still apply — only
the dates move.

---

## 2. WHERE THE CODEBASE ACTUALLY STANDS TODAY

### Frontend/ — real, ~4,900 LOC, working

| Item | Confirmed |
|---|---|
| Framework | React **19.2.7** (the Frontend README says 18 — README is wrong) |
| Routing | react-router-dom 7.18.1, 13 routes, all role-gated by `ProtectedRoute` |
| Charts | recharts 3.10 |
| Build | Vite 8.1 · Lint: oxlint |
| Tests | **None.** No test runner, no test script, no test files |
| Backend calls | **None.** No `fetch`, no axios, no API base URL anywhere |

**The four React contexts are your de-facto API contract.** Treat them as the spec:

| Context | Entities seeded | Mutators | Persistence |
|---|---|---|---|
| `AuthContext` | 5 hardcoded `DEMO_USERS`, plaintext passwords | `login`, `logout` | localStorage |
| `ComplaintsContext` | 8 complaints | `addComplaint`, `updateComplaint`, `updateStatus`, `cancelComplaint` | **in-memory, resets on reload** |
| `BulkPickupContext` | 3 pickups | `schedulePickup`, `updatePickup`, `cancelPickup` | localStorage |
| `OperationalContext` | 5 workers, 5 equipment, 5 vehicles, 3 feed posts | 9 mutators | localStorage |

**Integration head start:** `ComplaintsContext` and `BulkPickupContext` mutators were deliberately
written to return Promises, so their bodies can be swapped for `fetch()` without touching any
component. `OperationalContext`'s 9 mutators are **synchronous** — those need signature changes
too. Budget for that (task S2-C01).

**Two pure utils to port server-side verbatim:**
- `utils/duplicateDetection.js` — Haversine + Jaccard, thresholds 200 m / 0.6 / 0.35. Its own
  comment says it targets a `GET /complaints/nearby` endpoint. **No AI/ML.**
- `utils/collectionSchedule.js` — 4 ward timetables, nth-weekday-of-month math, 2 exceptions.

**Status enums already fixed by the UI — the backend must match these exactly:**
- Complaint: `Pending` / `In Progress` / `Resolved` / `Cancelled`
- Bulk pickup: `Requested` / `Scheduled` / `Collected` / `Cancelled`
- Worker: `On Duty` / `Off Duty` / `Available`
- Equipment: `Available` / `In Use` / `Maintenance`
- Vehicle: `Available` / `En Route` / `On Site` / `In Depot` / `Maintenance`

### Backend/ — scaffold only

Good bones, zero implementation. What exists: the layered folder tree
(`api/` → `services/` → `repositories/` → `models/`), a genuinely good architecture README,
`.env.example` with the right variables, `docker-compose.yml` with a working `db` service
(postgres:16), and a CI workflow skeleton.

What does **not** exist: any model, schema, repository, service, route, migration, or test.

### .github/workflows/backend-ci.yml

Triggers correctly on PR/push for `Backend/**`, spins up postgres:16, installs uv + Python 3.13 —
then every real step (`uv sync`, `ruff`, `black`, `alembic upgrade`, `pytest`) is commented out.
No frontend CI exists.

---

## 3. MASTER USER STORY LIST

33 stories from `Milestone_1_Deliverables.pdf`, given stable IDs. **Use these IDs everywhere** —
in the OpenAPI `x-user-story` field, in commit messages, in Jira, and in test case docs.

| ID | Doc ref | Story | Role | Sprint |
|---|---|---|---|---|
| US-01 | 1.1 | Report a garbage issue | Citizen | 1 |
| US-02 | 1.2 | Share the location of the issue | Citizen | 1 |
| US-03 | 1.3 | Upload a photo | Citizen | 1 |
| US-04 | 1.4 | Add additional information (description) | Citizen | 1 |
| US-05 | 2.1 | View similar complaints for a location | Admin | 1 |
| US-06 | 2.2 | Receive duplicate-complaint notification | Citizen | 1 (detect) / 2 (notify) |
| US-07 | 2.3 | View and manage all complaints | Ward Supervisor | 1 |
| US-08 | 3.1 | Report hazard information | Citizen | 1 |
| US-09 | 3.2 | Identify high-risk areas | Health Officer | 1 |
| US-10 | 3.3 | Report child safety concerns | Resident | 1 |
| US-11 | 3.4 | Receive hazard information before a task | Crew | 1 |
| US-12 | 4.1 | Identify waste type before assigning | Ward Supervisor | 1 |
| US-13 | 4.2 | Allocate workforce & equipment | Ward Supervisor | 1 |
| US-14 | 4.3 | Assign collection vehicle | Collection Supervisor | 1 |
| US-15 | 5.1 | Assign cleanup tasks to field workers | Ward Supervisor | 1 |
| US-16 | 5.2 | View assigned task locations | Crew | 1 |
| US-17 | 5.3 | View complaint details & photo | Crew | 1 |
| US-18 | 5.4 | Request additional assistance | Crew | 1 |
| US-19 | 6.1 | Upload completion photo | Crew | 2 |
| US-20 | 6.2 | Verify completed work | Admin | 2 |
| US-21 | 6.3 | Confirm task completion / close case | Ward Supervisor | 2 |
| US-22 | 7.1 | Track complaint progress | Citizen | 1 |
| US-23 | 7.2 | Receive resolution notification | Citizen | 2 |
| US-24 | 7.3 | Provide post-cleanup feedback | Citizen | 2 |
| US-25 | 8.1 | View public complaint / cleanup information | Citizen | 2 |
| US-26 | 8.2 | Monitor complaint trends by area | Admin | 2 |
| US-27 | 8.3 | Review performance reports | Senior Authority | 2 |
| US-28 | 9.1 | Report an overflowing bin | Resident | 2 |
| US-29 | 9.2 | Report delayed waste collection | Resident | 2 |
| US-30 | 9.3 | Request additional waste collection | Resident | 2 |
| US-31 | 10.1 | Schedule a bulk waste pickup | Resident | 2 |
| US-32 | 10.2 | View collection schedule | Resident | 2 |
| US-33 | 10.3 | Receive collection reminder | Resident | 2 |

**Note on US-06:** split across sprints. Sprint 1 delivers the *detection* endpoint (advisory
response at submit time). Sprint 2 delivers the persisted *notification* record.

---

## 4. USER STORY → FEATURE → API ENDPOINT MAPPING

### Sprint 1 endpoints (21)

| # | Method + path | Feature | Stories | Role | Build/Integrate |
|---|---|---|---|---|---|
| 1 | `POST /api/v1/auth/register` | Citizen self-registration | US-01 (prereq) | Public | Build |
| 2 | `POST /api/v1/auth/login` | JWT login, access + refresh | all | Public | Build (PyJWT) |
| 3 | `POST /api/v1/auth/refresh` | Rotate access token | all | Auth | Build (PyJWT) |
| 4 | `GET /api/v1/auth/me` | Current user profile | all | Auth | Build |
| 5 | `GET /api/v1/wards` | Ward reference list | US-02, US-13 | Auth | Build |
| 6 | `POST /api/v1/complaints` | Submit complaint (location, desc, hazard, coords, category) | US-01, 02, 04, 08, 10 | Citizen | Build |
| 7 | `POST /api/v1/complaints/{id}/photo` | Attach evidence photo | US-03 | Citizen | Build |
| 8 | `GET /api/v1/complaints` | List + filter + paginate | US-07, US-12 | Admin/Crew | Build |
| 9 | `GET /api/v1/complaints/{id}` | Complaint detail | US-17, US-22 | Auth | Build |
| 10 | `PATCH /api/v1/complaints/{id}/status` | Status transition | US-07 | Admin | Build |
| 11 | `POST /api/v1/complaints/{id}/cancel` | Citizen withdraws (Pending only) | US-07 | Citizen | Build |
| 12 | `POST /api/v1/complaints/duplicate-check` | Pre-submit advisory duplicate scan | US-06 | Citizen | Build |
| 13 | `GET /api/v1/complaints/{id}/duplicates` | Similar complaints for a case | US-05 | Admin | Build |
| 14 | `GET /api/v1/complaints/high-risk` | Hazard-weighted hotspot list | US-09 | Admin | Build |
| 15 | `POST /api/v1/tasks` | Create assignment (crew + vehicle + equipment) | US-13, 14, 15 | Admin | Build |
| 16 | `GET /api/v1/tasks` | Crew's assigned task list | US-16 | Crew/Admin | Build |
| 17 | `GET /api/v1/tasks/{id}` | Task detail w/ hazard + complaint + location | US-11, 16, 17 | Crew/Admin | Build |
| 18 | `PATCH /api/v1/tasks/{id}/status` | Crew advances task state | US-16 | Crew | Build |
| 19 | `POST /api/v1/tasks/{id}/assistance` | Crew requests extra resources | US-18 | Crew | Build |
| 20 | `GET /api/v1/workers` · `GET /api/v1/equipment` | Allocatable workforce & tools | US-13 | Admin | Build |
| 21 | `GET /api/v1/vehicles` · `PATCH /api/v1/vehicles/{id}` | Fleet list + dispatch | US-14 | Admin | Build |

### Sprint 2 endpoints (19)

| # | Method + path | Feature | Stories | Role | Build/Integrate |
|---|---|---|---|---|---|
| 22 | `POST /api/v1/tasks/{id}/complete` | Upload proof-of-work photo, close task | US-19 | Crew | Build |
| 23 | `PATCH /api/v1/complaints/{id}/verify` | Admin reviews completed work | US-20 | Admin | Build |
| 24 | `PATCH /api/v1/complaints/{id}/close` | Supervisor confirms resolution | US-21 | Admin | Build |
| 25 | `GET /api/v1/notifications` | In-app notification inbox | US-06, US-23 | Auth | Build |
| 26 | `PATCH /api/v1/notifications/{id}/read` | Mark read | US-23 | Auth | Build |
| 27 | `POST /api/v1/complaints/{id}/feedback` | Post-cleanup rating + comment | US-24 | Citizen | Build |
| 28 | `GET /api/v1/feed` | Transparency feed, ward-filterable | US-25 | Auth | Build |
| 29 | `POST /api/v1/feed/{id}/applaud` | Applaud a post | US-25 | Auth | Build |
| 30 | `POST /api/v1/feed/{id}/comments` | Comment on a post | US-25 | Auth | Build |
| 31 | `GET /api/v1/reports/public` | Public cleanup stats | US-25 | Auth | Build |
| 32 | `GET /api/v1/reports/trends` | Status/hazard/time-series rollups | US-26 | Admin | Build |
| 33 | `GET /api/v1/reports/performance` | Avg resolution time, crew perf | US-27 | Authority | Build |
| 34 | `POST /api/v1/bulk-pickups` | Request bulk pickup + fee quote | US-31 | Citizen | Build |
| 35 | `GET /api/v1/bulk-pickups` | List own / all pickups | US-31 | Auth | Build |
| 36 | `PATCH /api/v1/bulk-pickups/{id}` · `/cancel` | Reschedule / withdraw | US-31 | Citizen/Admin | Build |
| 37 | `POST /api/v1/bulk-pickups/{id}/assign` | Assign crew + vehicle | US-31 | Admin | Build |
| 38 | `GET /api/v1/schedule` | Per-ward collection timetable | US-32 | Auth | Build |
| 39 | `GET /api/v1/schedule/reminders` | Upcoming pickups for the user's ward | US-33 | Citizen | Build |
| 40 | `POST /api/v1/complaints/{id}/classify` | **GenAI** hazard auto-classification | US-08, US-09 | Admin | **Integrate (Claude API)** |

**Note on US-28/29/30** (overflowing bin, delayed collection, extra collection): your Sprint 2 CSV
proposed separate endpoints (`POST /complaints/overflow`, `POST /complaints/delay`). **Don't do
that** — it triples the code path for what is one field. Implement as a `category` enum on the
existing `POST /complaints`: `garbage_dump` | `overflowing_bin` | `delayed_collection` |
`extra_collection`. One endpoint, four categories, three stories satisfied. (Task S2-A18.)

---

## 5. APIs WE BUILD vs APIs WE INTEGRATE

Rubric deliverable #6 requires this split explicitly. Right now the repo has **zero** external
integrations, and both "smart" features (duplicate detection, schedule math) are deliberately
plain algorithms. That would leave this rubric line empty — so the table below includes
integrations worth adding.

### 5a. APIs created by us (40 endpoints)

All 40 endpoints in section 4 are designed, specified, and implemented by the team. Grouped:
Auth (4), Wards (1), Complaints (9), Tasks (6), Resources (5), Verification (3),
Notifications (2), Feedback (1), Feed (3), Reports (3), Bulk pickup (4), Schedule (2).

### 5b. Integrated from libraries / external / GenAI

| What | Source | Type | Used for | Sprint |
|---|---|---|---|---|
| **PyJWT** | `pyjwt` (PyPI) | Library | JWT sign/verify for all auth | 1 |
| **bcrypt** | `bcrypt` (PyPI) | Library | Password hashing | 1 |
| **FastAPI OpenAPI generator** | FastAPI built-in | Library | Auto-serves Swagger UI at `/docs` + `/openapi.json`; cross-checked against our hand-written YAML | 1 |
| **SQLAlchemy 2.0 + Alembic** | PyPI | Library | ORM + migrations | 1 |
| **Browser Geolocation API** | `navigator.geolocation` (W3C) | External/browser | US-02 — already wired in `ReportComplaint.jsx` | 1 |
| **Nominatim reverse geocoding** | OpenStreetMap public API | **External REST API** | Turn lat/lng into a human address on complaint submit | 2 |
| **Claude API — hazard classification** | Anthropic `claude-sonnet-5` | **GenAI API** | Read complaint description (+photo) → suggest hazard type + severity, feeding US-08/US-09 | 2 |
| **recharts** | npm | Library | Frontend charts for US-26/27 | done |

**On the two Sprint 2 integrations:** both are small and both are genuinely useful, not
box-ticking. Nominatim is free, needs no API key, and just requires a `User-Agent` header and
≤1 req/sec. The Claude call is one HTTP request with a structured-output schema; wrap it so a
timeout or error falls back to the citizen's manually-selected hazard rather than failing the
request. Budget an `ANTHROPIC_API_KEY` env var and **do not commit it**.

---

## 6. SPRINT 1 SCOPE

**Theme:** Foundation + the complaint-to-assignment core loop.
**Dates:** Jul 23 – Aug 2 (per Option A) · **Endpoints:** 21 · **Total effort:** 164 points

**In scope:**
- Full runnable FastAPI app: config, DB session, migrations, middleware, error envelope, CI green
- JWT auth with RBAC (`citizen` / `crew` / `admin` / `authority`)
- Complaint lifecycle: create, read, list+filter+paginate, status transition, cancel, photo upload
- Duplicate detection ported from the frontend util (advisory, non-blocking)
- High-risk area query (US-09)
- Task assignment: crew + vehicle + equipment allocation, crew status updates, assistance requests
- Resource read/update endpoints (workers, vehicles, equipment)
- `openapi.yaml` for all 21 endpoints, Spectral-clean
- `test_cases.md` in the 5-column format for all 21
- pytest suites: happy path + ≥2 failure/edge cases per endpoint
- Frontend: `ComplaintsContext` and `AuthContext` switched from mock to live API

**Explicitly out of scope (deferred to Sprint 2):** verification/close, notifications, feedback,
reports, transparency feed, bulk pickup, collection schedule, GenAI classification.

**Sprint 1 database tables (migration 0001):** `users`, `wards`, `complaints`,
`complaint_status_history`, `workers`, `vehicles`, `equipment`, `tasks`, `task_workers`,
`task_equipment`. Ten tables. Sprint 2 adds six more in migration 0002.

---

## 7. SPRINT 2 SCOPE

**Theme:** Close the loop — verification, citizen feedback, reporting, community services.
**Dates:** Aug 3 – Aug 12 · **Endpoints:** 19 · **Total effort:** 133 points

**In scope:**
- Verification chain: crew completion photo → admin verify → supervisor close
- Auto-generated `TransparencyPost` on close (this is what makes US-25 real rather than seeded)
- In-app notifications (duplicate detected, complaint resolved)
- Citizen feedback capture
- Three reports endpoints backing the existing `ReportsTrends.jsx` dashboard
- Bulk pickup lifecycle including fee calculation and crew/vehicle assignment
- Collection schedule + reminders (port of `collectionSchedule.js`)
- Community categories for US-28/29/30
- Two external integrations: Nominatim reverse geocoding, Claude hazard classification
- Full frontend integration: `OperationalContext` (9 mutators, sync→async) + `BulkPickupContext`
- `openapi.yaml`, `test_cases.md`, pytest for all 19 endpoints
- Coverage report ≥70% on `app/services`

**Sprint 2 tables (migration 0002):** `feedback`, `transparency_posts`, `post_comments`,
`notifications`, `bulk_pickups`, `collection_schedules`.

---

## 8. DEPENDENCY GRAPH & ORDERING RULES

### Hard blockers — nothing else can start until these land

```
S1-F01 (pin deps)
   └─> S1-F02 (config) ──> S1-F03 (db base + session)
                              └─> S1-F08 (alembic + migration 0001)
                                     └─> everything that touches the DB
S1-F04 (security: bcrypt + JWT)
   └─> S1-A08 (deps.py: get_current_user, require_role)
          └─> every protected route (i.e. all 20 non-login endpoints)
S1-F05 (exceptions + error envelope)
   └─> every route (they all return the standard error shape)
S1-F11 (conftest fixtures)
   └─> every pytest file
```

**Day-1 rule: S1-F01 → F02 → F03 → F04 → F05 → F08 → F11 must be merged within the first 24
hours.** These are assigned across three people specifically so they can be done in parallel and
merged fast. If they slip, the entire sprint slips 1:1.

### Sequencing constraints between owners

| This must land first | Before this can start | Owners involved | Why |
|---|---|---|---|
| S1-F04 security | S1-A08 deps.py | Sagnik → Sagnik | Same owner, no handoff risk |
| S1-A08 deps.py | All protected routes | Sagnik → Vishal, Nitin, Pankaj, Jatin | **Highest-risk handoff in the sprint** |
| S1-M02 complaint model | S1-M03 task model | Vishal → Nitin | Task FKs to complaint |
| S1-M04 resource models | S1-S04 task service | Nitin → Nitin | Assignment needs worker/vehicle/equipment |
| S1-U01/U02 geo + text utils | S1-S03 duplicate service | Jatin → Jatin | Same owner |
| S1-S02 complaint service | S1-S04 task service | Vishal → Nitin | Assignment reads complaint state |
| S1-F11 conftest | All S1-P* pytest tasks | Jatin → everyone | Second-highest-risk handoff |
| S1-Y01/Y02 OpenAPI YAML | Route implementation | Pankaj → all devs | **Contract-first: write the YAML before the code** |
| S2-A03 close endpoint | S2-A04 auto TransparencyPost | Nitin → Jatin | Post is generated on close |
| Sprint 1 tasks API | S2-A01 completion photo | Nitin → Nitin | Extends the task record |

### Mitigation for the two risky handoffs

- **`deps.py` (S1-A08):** Sagnik publishes the *function signatures* (`get_db`,
  `get_current_user`, `require_role(*roles)`) as a stub PR on **day 1** before the bodies are
  written. Everyone else codes against the signatures immediately; the bodies land within hours.
- **`conftest.py` (S1-F11):** Jatin publishes fixture names (`client`, `db`, `citizen_token`,
  `admin_token`, `crew_token`, `seed_ward`, `seed_complaint`) on **day 1** the same way.

---

## 9. SPRINT 1 — FULL TASK LIST WITH OWNERS

**Effort key:** 1 point ≈ 2 hours. Type: `Infra` / `API build` / `Integration` / `Test design` /
`Pytest` / `Review` / `Frontend` / `Docs-PM`.

### 9a. Foundation (Day 1 — must land first)

| ID | Task | Type | Owner | Pts | Depends on |
|---|---|---|---|---|---|
| S1-F01 | Pin all deps in `pyproject.toml`, generate lockfile, verify `uv sync` | Infra | Vishal | 2 | — |
| S1-F02 | `core/config.py` — Settings from env (DB, JWT, CORS, upload, thresholds) | Infra | Vishal | 2 | F01 |
| S1-F03 | `db/base.py` (Base + TimestampMixin) and `db/session.py` (engine, `get_db`) | Infra | Vishal | 2 | F02 |
| S1-F04 | `core/security.py` — bcrypt hash/verify, JWT access+refresh create/decode | Infra | Sagnik | 3 | F02 |
| S1-F05 | `core/exceptions.py` — typed errors + handlers + standard error envelope | Infra | Sagnik | 3 | — |
| S1-F06 | `middleware/` — request-id, access log; CORS wiring | Infra | Nitin | 2 | F02 |
| S1-F07 | `main.py` — app factory, middleware, router include, exception handlers | Infra | Vishal | 2 | F03, F05 |
| S1-F08 | Alembic init + `env.py` reading settings + migration 0001 (10 tables) | Infra | Nitin | 3 | F03, all M0* |
| S1-F09 | Enable `api` service in docker-compose; verify Dockerfile builds | Infra | Pankaj | 2 | F07 |
| S1-F10 | Uncomment + fix all CI steps in `backend-ci.yml`; get it green | Infra | Pankaj | 2 | F01, F11 |
| S1-F11 | `tests/conftest.py` — TestClient, SQLite test DB, token + data fixtures | Infra | Jatin | 4 | F03, F07 |
| S1-F12 | Seed script — 4 wards, 5 demo users, 5 workers, 5 vehicles, 5 equipment | Infra | Jatin | 3 | F08 |

### 9b. Models & schemas

| ID | Task | Type | Owner | Pts | Depends on |
|---|---|---|---|---|---|
| S1-M01 | Models: `User`, `Ward` | API build | Sagnik | 2 | F03 |
| S1-M02 | Models: `Complaint` + `ComplaintStatusHistory` | API build | Vishal | 3 | F03, M01 |
| S1-M03 | Models: `Task`, `task_workers`, `task_equipment` join tables | API build | Nitin | 3 | M02, M04 |
| S1-M04 | Models: `Worker`, `Vehicle`, `Equipment` | API build | Nitin | 2 | F03, M01 |
| S1-M05 | Schemas: auth (Login/Token/Register), user, ward | API build | Sagnik | 2 | M01 |
| S1-M06 | Schemas: complaint Create/Update/Read/Filter | API build | Vishal | 3 | M02 |
| S1-M07 | Schemas: task + resource DTOs | API build | Nitin | 2 | M03, M04 |
| S1-M08 | Schemas: common — pagination envelope, error envelope | API build | Pankaj | 1 | — |

### 9c. Repositories & utils

| ID | Task | Type | Owner | Pts | Depends on |
|---|---|---|---|---|---|
| S1-R01 | `repositories/base.py` — generic CRUD | API build | Sagnik | 2 | F03 |
| S1-R02 | `repositories/user.py`, `ward.py` | API build | Sagnik | 2 | R01, M01 |
| S1-R03 | `repositories/complaint.py` — filters, pagination, sort | API build | Vishal | 3 | R01, M02 |
| S1-R04 | `repositories/task.py` | API build | Nitin | 2 | R01, M03 |
| S1-R05 | `repositories/resource.py` | API build | Nitin | 2 | R01, M04 |
| S1-U01 | `utils/geo.py` — Haversine (port of `duplicateDetection.js`) | API build | Jatin | 2 | — |
| S1-U02 | `utils/text.py` — tokenize + stopwords + Jaccard similarity | API build | Jatin | 2 | — |

### 9d. Services

| ID | Task | Type | Owner | Pts | Depends on |
|---|---|---|---|---|---|
| S1-S01 | `services/auth.py` — register, login, refresh, me | API build | Sagnik | 3 | F04, R02 |
| S1-S02 | `services/complaint.py` — CRUD + status state machine + cancel rules | API build | Vishal | 4 | R03 |
| S1-S03 | `services/duplicate.py` — scoring, ranking, thresholds from config | API build | Jatin | 3 | U01, U02, R03 |
| S1-S04 | `services/task.py` — assignment orchestration, resource availability | API build | Nitin | 4 | R04, R05, S02 |
| S1-S05 | `services/resource.py` — worker/vehicle/equipment status updates | API build | Nitin | 2 | R05 |

### 9e. API routes

| ID | Task | Type | Owner | Pts | Depends on |
|---|---|---|---|---|---|
| S1-A08 | `api/deps.py` — `get_db`, `get_current_user`, `require_role(*roles)` | API build | Sagnik | 3 | F04 |
| S1-A01 | `routes/auth.py` — endpoints 1–4 | API build | Sagnik | 3 | S01, A08 |
| S1-A02 | `routes/wards.py` — endpoint 5 | API build | Sagnik | 1 | R02, A08 |
| S1-A03 | `routes/complaints.py` — endpoints 6, 8, 9, 10, 11 | API build | Vishal | 4 | S02, A08, Y01 |
| S1-A05 | `routes/complaints.py` — endpoint 7 (photo upload, mime+size validation) | API build | Vishal | 2 | A03 |
| S1-A04 | `routes/complaints.py` — endpoints 12, 13, 14 (duplicates, high-risk) | API build | Jatin | 3 | S03, A08 |
| S1-A06 | `routes/tasks.py` — endpoints 15–19 | API build | Nitin | 4 | S04, A08, Y02 |
| S1-A07 | `routes/resources.py` — endpoints 20, 21 | API build | Pankaj | 3 | S05, A08 |
| S1-A09 | `api/v1/router.py` — aggregate all routers | API build | Vishal | 1 | all A0* |

### 9f. API documentation (contract-first — start these Day 1, before routes)

| ID | Task | Type | Owner | Pts | Depends on |
|---|---|---|---|---|---|
| S1-Y01 | `docs/sprint-1/openapi.yaml` — auth, wards, complaints (14 endpoints) | Docs-PM | Pankaj | 4 | M08 |
| S1-Y02 | `docs/sprint-1/openapi.yaml` — tasks, resources (7 endpoints) | Docs-PM | Pankaj | 3 | M08 |
| S1-Y03 | Spectral ruleset + CI lint job; verify Swagger Editor renders clean | Docs-PM | Pankaj | 2 | Y01, Y02 |

Every path object must carry: `summary`, `description`, `operationId`, `x-user-story` (the US-xx
IDs), request schema, 2xx response schema, and explicit `400/401/403/404/409/422` responses using
the shared error envelope.

### 9g. Test case design (5-column format)

| ID | Task | Type | Owner | Pts | Depends on |
|---|---|---|---|---|---|
| S1-T01 | `docs/sprint-1/test_cases.md` — auth + wards (5 endpoints) | Test design | Jatin | 3 | Y01 |
| S1-T02 | `docs/sprint-1/test_cases.md` — complaints (9 endpoints) | Test design | Jatin | 4 | Y01 |
| S1-T03 | `docs/sprint-1/test_cases.md` — tasks + resources (7 endpoints) | Test design | Pankaj | 4 | Y02 |

Required columns, exactly: `API being tested | Inputs | Expected Output | Actual Output | Result`.
Minimum 4 cases per endpoint (1 happy path, 1 validation failure, 1 auth/RBAC failure, 1 edge
case). **Leave `Actual Output` blank until the pytest run** — fill it from real output, and keep
at least one row where actual ≠ expected plus the fix, to evidence debugging value (rubric asks
for this).

### 9h. Pytest implementation

| ID | Task | Type | Owner | Pts | Depends on |
|---|---|---|---|---|---|
| S1-P01 | `tests/api/test_auth.py` | Pytest | Sagnik | 3 | A01, F11, T01 |
| S1-P02 | `tests/api/test_complaints.py` | Pytest | Vishal | 4 | A03, A05, F11, T02 |
| S1-P03 | `tests/api/test_tasks.py` | Pytest | Nitin | 4 | A06, F11, T03 |
| S1-P04 | `tests/api/test_resources.py` | Pytest | Jatin | 2 | A07, F11, T03 |
| S1-P05 | `tests/unit/test_duplicate_detection.py` — parity with the JS util | Pytest | Jatin | 3 | S03, U01, U02 |
| S1-P06 | `tests/unit/test_security.py` — hashing, token expiry, wrong-type token | Pytest | Sagnik | 2 | F04 |
| S1-P07 | `tests/integration/test_complaint_to_task_flow.py` — end-to-end | Pytest | Nitin | 3 | A03, A06 |

### 9i. Frontend integration, review, and sprint close

| ID | Task | Type | Owner | Pts | Depends on |
|---|---|---|---|---|---|
| S1-C05 | Swap `ComplaintsContext` mutators to `fetch()` against live API | Frontend | Vishal | 4 | A03 |
| S1-C06 | Swap `AuthContext` to real JWT login; token storage + refresh on 401 | Frontend | Jatin | 3 | A01 |
| S1-C01 | Code review every PR; enforce layer boundaries and comment quality | Review | Sagnik | 4 | ongoing |
| S1-C07 | PM: board setup, branch protection, labels, PR template, CODEOWNERS | Docs-PM | Pankaj | 3 | — |
| S1-C02 | Run Sprint 1 demo with end users; capture feedback verbatim | Docs-PM | Pankaj | 2 | all |
| S1-C03 | Write feedback summary + Sprint 2 plan section | Docs-PM | Pankaj | 2 | C02 |
| S1-C04 | Compile Sprint 1 submission (YAML, code, test cases, pytest output, feedback) | Docs-PM | Pankaj | 3 | all |

---

## 10. SPRINT 2 — FULL TASK LIST WITH OWNERS

### 10a. Foundation

| ID | Task | Type | Owner | Pts | Depends on |
|---|---|---|---|---|---|
| S2-F01 | Alembic migration 0002 — 6 new tables | Infra | Nitin | 3 | S2-F02/03/04 |
| S2-F02 | Models: `Feedback`, `Notification` | API build | Sagnik | 2 | S1 done |
| S2-F03 | Models: `TransparencyPost`, `PostComment` | API build | Jatin | 2 | S1 done |
| S2-F04 | Models: `BulkPickup`, `CollectionSchedule` | API build | Vishal | 3 | S1 done |
| S2-F05 | Upload hardening — size cap, mime sniff, path-traversal guard, static mount | Infra | Sagnik | 3 | S1-A05 |

### 10b. Verification & accountability (US-19, 20, 21)

| ID | Task | Type | Owner | Pts | Depends on |
|---|---|---|---|---|---|
| S2-A01 | `POST /tasks/{id}/complete` — completion photo + waste-removed capture | API build | Nitin | 4 | F05 |
| S2-A02 | `PATCH /complaints/{id}/verify` — admin review | API build | Nitin | 3 | A01 |
| S2-A03 | `PATCH /complaints/{id}/close` — supervisor confirm, stamps `resolvedAt` | API build | Nitin | 2 | A02 |
| S2-A04 | Auto-generate `TransparencyPost` on close (before/after photos) | API build | Jatin | 3 | A03, F03 |

### 10c. Notifications & feedback (US-06, 23, 24)

| ID | Task | Type | Owner | Pts | Depends on |
|---|---|---|---|---|---|
| S2-A05 | Notification emitter — on duplicate detected, on complaint resolved | API build | Sagnik | 3 | F02, A03 |
| S2-A06 | `GET /notifications` + `PATCH /notifications/{id}/read` | API build | Sagnik | 3 | A05 |
| S2-A07 | `POST /complaints/{id}/feedback` — rating + comment, resolved-only | API build | Sagnik | 3 | F02, A03 |

### 10d. Reports & transparency feed (US-25, 26, 27)

| ID | Task | Type | Owner | Pts | Depends on |
|---|---|---|---|---|---|
| S2-A08 | `GET /reports/trends` — status, hazard, time series (backs `ReportsTrends.jsx`) | API build | Vishal | 4 | S1 done |
| S2-A09 | `GET /reports/performance` — avg resolution days, crew/ward perf | API build | Vishal | 3 | A03 |
| S2-A10 | `GET /reports/public` — public cleanup stats | API build | Sagnik | 2 | A04 |
| S2-A11 | `GET /feed` — paginated, ward filter | API build | Jatin | 3 | F03 |
| S2-A12 | `POST /feed/{id}/applaud` + `POST /feed/{id}/comments` | API build | Jatin | 3 | A11 |

### 10e. Bulk pickup & collection schedule (US-31, 32, 33)

| ID | Task | Type | Owner | Pts | Depends on |
|---|---|---|---|---|---|
| S2-A13 | `POST /bulk-pickups` + `GET /bulk-pickups` incl. fee calculation | API build | Vishal | 4 | F04 |
| S2-A14 | `PATCH /bulk-pickups/{id}` + `/cancel` with state rules | API build | Vishal | 3 | A13 |
| S2-A15 | `POST /bulk-pickups/{id}/assign` — crew + vehicle | API build | Nitin | 3 | A13 |
| S2-A16 | `GET /schedule` — port `collectionSchedule.js` nth-weekday math | API build | Jatin | 3 | F04 |
| S2-A17 | `GET /schedule/reminders` — upcoming pickups for the user's ward | API build | Jatin | 3 | A16 |

### 10f. Community categories & GenAI integration

| ID | Task | Type | Owner | Pts | Depends on |
|---|---|---|---|---|---|
| S2-A18 | Complaint `category` enum for US-28/29/30 + validation + filter support | API build | Pankaj | 2 | S1-A03 |
| S2-A19 | `POST /complaints/{id}/classify` — Claude API hazard classification, with graceful fallback | **Integration** | Pankaj | 4 | S1-A03 |

### 10g. Documentation, tests, integration, close

| ID | Task | Type | Owner | Pts | Depends on |
|---|---|---|---|---|---|
| S2-Y01 | `docs/sprint-2/openapi.yaml` — verification, feedback, notifications | Docs-PM | Pankaj | 4 | — |
| S2-Y02 | `docs/sprint-2/openapi.yaml` — reports, feed, bulk, schedule, classify | Docs-PM | Pankaj | 4 | — |
| S2-T01 | `test_cases.md` — verification & feedback | Test design | Jatin | 4 | Y01 |
| S2-T02 | `test_cases.md` — reports & feed | Test design | Pankaj | 3 | Y02 |
| S2-T03 | `test_cases.md` — bulk pickup & schedule | Test design | Nitin | 3 | Y02 |
| S2-P01 | `tests/api/test_verification.py` | Pytest | Nitin | 4 | A01-A03 |
| S2-P02 | `tests/api/test_feedback_notifications.py` | Pytest | Sagnik | 3 | A05-A07 |
| S2-P03 | `tests/api/test_reports.py` | Pytest | Vishal | 3 | A08-A10 |
| S2-P04 | `tests/api/test_bulk_pickup.py` | Pytest | Sagnik | 3 | A13-A15 |
| S2-P05 | `tests/api/test_schedule_feed.py` | Pytest | Jatin | 3 | A11, A16 |
| S2-P06 | `tests/integration/test_full_lifecycle.py` — report → assign → complete → verify → close → feedback | Pytest | Nitin | 4 | all |
| S2-C01 | Wire `OperationalContext` → API (9 mutators, **sync→async signature change**) | Frontend | Jatin | 5 | A11, S1-A07 |
| S2-C02 | Wire `BulkPickupContext` → API | Frontend | Vishal | 3 | A13 |
| S2-C03 | Wire `ReportsTrends.jsx` → `/reports/trends` | Frontend | Vishal | 3 | A08 |
| S2-C04 | Code review every PR | Review | Sagnik | 4 | ongoing |
| S2-C08 | Coverage report ≥70% on `app/services`; publish summary | Review | Sagnik | 2 | all P* |
| S2-C05 | Sprint 2 demo with end users | Docs-PM | Pankaj | 2 | all |
| S2-C06 | Feedback summary + Milestone 5 plan | Docs-PM | Pankaj | 2 | C05 |
| S2-C07 | Compile Sprint 2 submission package | Docs-PM | Pankaj | 3 | all |

---

## 11. WORKLOAD BALANCE CHECK

| Person | Nominal role | Sprint 1 pts | Sprint 2 pts | **Total** | vs. average |
|---|---|---|---|---|---|
| Pankaj Joshi | Product Manager / Scrum Master | 31 | 24 | **55** | −7% |
| Vishal Vinayak Gaikwad | Frontend / Backend Dev | 35 | 26 | **61** | +3% |
| Sagnik Halder | Code Reviewer / Backend Dev | 33 | 28 | **61** | +3% |
| Nitin Gupta | Backend / Tester | 33 | 26 | **59** | −1% |
| Jatin Chakrabarty | Tester / Frontend Dev | 32 | 29 | **61** | +3% |
| | **Total** | **164** | **133** | **297** | avg 59.4 |

**Spread: −7% to +3%** — inside your ±10–15% target.

**Everyone gets a genuine mix** — nobody is stuck doing only one type of work:

| Person | API build | Test design | Pytest | Frontend | Infra | Review | Docs-PM | Integration |
|---|---|---|---|---|---|---|---|---|
| Pankaj | ✓ (4 ep) | ✓ | — | — | ✓ | — | ✓ | ✓ GenAI |
| Vishal | ✓ (16 ep) | — | ✓ | ✓ | ✓ | — | — | — |
| Sagnik | ✓ (12 ep) | — | ✓ | — | ✓ | ✓ | — | — |
| Nitin | ✓ (12 ep) | ✓ | ✓ | — | ✓ | — | — | — |
| Jatin | ✓ (11 ep) | ✓ | ✓ | ✓ | ✓ | — | — | — |

Notes on the allocation:
- **Pankaj is deliberately below average on points** because Scrum Master overhead (standups,
  board grooming, unblocking, demo coordination) isn't captured in story points. His real load is
  comparable. He still owns 4 endpoints, the GenAI integration, all OpenAPI YAML, and one test
  case document — he is not a pure coordinator.
- **Sagnik owns code review** as his nominal role, but that's only 8 of his 61 points. He also
  owns the entire auth vertical (security → deps → service → routes → tests), which is the
  highest-leverage backend work in Sprint 1.
- **Jatin is nominally "Tester"** but owns `conftest.py`, both pure utils, the duplicate detection
  service, the transparency feed, the collection schedule, and the heaviest frontend integration
  task. Roughly half his load is production code.
- **Nitin is nominally "Backend/Tester"** and gets the task-assignment vertical plus both
  end-to-end integration tests — the two hardest pieces of test engineering.

---

## 12. DELIVERABLES CHECKLIST

Rubric weights: API creation/integration & user-story mapping (15) · API implementation quality
(20) · test case design (20) · pytest coverage (5).

### Sprint 1 submission

- [ ] `docs/sprint-1/openapi.yaml` — 21 endpoints, Swagger-compatible, Spectral-clean *(Pankaj)*
  - [ ] Every endpoint has `description` and `summary`
  - [ ] Every endpoint has `x-user-story` listing US-xx IDs
  - [ ] Every endpoint documents 400/401/403/404/409/422 with the shared error schema
- [ ] Backend implementation for all 21 endpoints, commented, validated, error-handled *(Vishal, Sagnik, Nitin, Jatin, Pankaj)*
- [ ] `docs/sprint-1/test_cases.md` — 5 columns, ≥4 cases/endpoint (~84 cases) *(Jatin, Pankaj)*
  - [ ] `Actual Output` filled from real runs, not copied from Expected
  - [ ] ≥1 documented case where actual ≠ expected, with the fix noted
- [ ] pytest suites — happy path + ≥2 failure/edge per endpoint, CI green *(all)*
- [ ] `docs/sprint-1/FEEDBACK.md` — demo feedback + Sprint 2 plan *(Pankaj)*
- [ ] `docs/API_INVENTORY.md` — built vs integrated split (section 5 of this doc) *(Pankaj)*

### Sprint 2 submission

- [ ] `docs/sprint-2/openapi.yaml` — 19 endpoints *(Pankaj)*
- [ ] Backend implementation for all 19 endpoints *(all)*
- [ ] `docs/sprint-2/test_cases.md` — ~76 cases *(Jatin, Pankaj, Nitin)*
- [ ] pytest suites incl. full-lifecycle integration test *(all)*
- [ ] Coverage report ≥70% on `app/services` *(Sagnik)*
- [ ] `docs/sprint-2/FEEDBACK.md` — demo feedback + Milestone 5 plan *(Pankaj)*
- [ ] Updated `API_INVENTORY.md` with the two external integrations *(Pankaj)*

### Feedback template — copy into `docs/sprint-N/FEEDBACK.md` and fill after the demo

```markdown
# Sprint N — User Feedback & Next Sprint Plan

## Demo details
- Date: | Duration: | Facilitator:
- Features demonstrated:
- Participants (role, not just name):

## Feedback received
| # | Participant role | Feature | Feedback (verbatim) | Type (bug/UX/feature/perf) | Severity | Action |
|---|---|---|---|---|---|---|
| 1 | | | | | | |

## What worked
## What didn't
## Bugs found during demo
| # | Endpoint | Symptom | Root cause | Fixed in |
|---|---|---|---|---|

## Plan for next sprint
| Priority | Item | Origin (feedback # / backlog) | Owner | Est. |
|---|---|---|---|---|

## Scope changes agreed
## Velocity: planned N pts / completed N pts
```

---

## 13. PM SETUP

This section is for Pankaj (task S1-C07). Everything below is concrete and runnable.

### 13.1 Fix branch protection — `main` is currently UNPROTECTED

Your Backend README claims *"`main` is protected and always deployable."* It is not — the GitHub
API reports `"protected": false`. Anyone can push or force-push to `main` today.

```bash
gh api -X PUT repos/pankuzj/MAY2026-Team-028/branches/main/protection \
  --input - <<'JSON'
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["quality", "frontend", "openapi-lint"]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
JSON
```

Add the status check contexts only *after* those CI jobs exist and have run once, or PRs will
block on checks that never report.

### 13.2 Project board

You already use Jira (epics SE-may-028…031) mirrored to Trello. Two options:

**Option A — stay on Jira (recommended, no migration cost).** Your two CSVs are already in Jira
import format. Re-import them with the `Assignee` column filled from sections 9 and 10 of this
document — it is currently empty in both files, which is why nothing is assigned. Add a
`Story Points` column with the point values from this plan.

**Option B — consolidate onto GitHub Projects** so tasks and PRs live in one place:

```bash
gh project create --owner pankuzj --title "SmartSweep Sprint 1"
# then add fields: Status (Todo/In Progress/In Review/Done), Owner, Points, Sprint, User Story
```

Whichever you pick, **use one board, not two.** A Jira board plus a Trello mirror plus GitHub
issues is three places for the same truth, and the rubric asks for evidence of issue tracking —
easier to screenshot one board that is actually current.

### 13.3 Labels, PR template, CODEOWNERS

```bash
gh label create "sprint-1"   --color 0E8A16
gh label create "sprint-2"   --color 1D76DB
gh label create "api-build"  --color 5319E7
gh label create "test"       --color FBCA04
gh label create "infra"      --color 006B75
gh label create "frontend"   --color D93F0B
gh label create "blocked"    --color B60205
```

`.github/pull_request_template.md`:

```markdown
## What
## User stories covered
US-xx, US-yy
## Task ID
S1-Axx
## Checklist
- [ ] Matches `openapi.yaml` (path, schema, status codes)
- [ ] Input validation + error handling on every path
- [ ] Layer boundaries respected (routes → services → repositories)
- [ ] Tests added; `pytest` green locally
- [ ] `ruff` + `black` clean
```

`.github/CODEOWNERS` — routes review to Sagnik automatically:

```
/Backend/app/       @sagnik-gh-username
/Backend/tests/     @nitin-gh-username
/Frontend/          @jatin-gh-username
/docs/              @pankuzj
```

### 13.4 CI workflows to set up

You have one workflow, fully stubbed. You need three.

**1. `backend-ci.yml` — uncomment the real steps (task S1-F10).** The scaffold is correct; just
enable the body:

```yaml
      - run: uv sync --all-extras
      - run: uv run ruff check .
      - run: uv run black --check .
      - run: uv run alembic upgrade head
        env:
          DATABASE_URL: postgresql+psycopg://smartsweep:smartsweep@localhost:5432/smartsweep_test
      - run: uv run pytest --cov=app --cov-report=term-missing --cov-fail-under=70
        env:
          DATABASE_URL: postgresql+psycopg://smartsweep:smartsweep@localhost:5432/smartsweep_test
```

**2. `frontend-ci.yml` — new.** Nothing checks the frontend today:

```yaml
name: Frontend CI
on:
  pull_request: { paths: ["Frontend/**"] }
  push: { branches: [main], paths: ["Frontend/**"] }
defaults: { run: { working-directory: Frontend } }
jobs:
  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '22', cache: 'npm', cache-dependency-path: Frontend/package-lock.json }
      - run: npm ci
      - run: npm run lint
      - run: npm run build
```

**3. `openapi-lint.yml` — new.** The rubric weights API docs at 15 points; lint them:

```yaml
name: OpenAPI Lint
on:
  pull_request: { paths: ["docs/**/openapi.yaml"] }
jobs:
  openapi-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npx --yes @stoplight/spectral-cli lint "docs/**/openapi.yaml" --ruleset .spectral.yaml
```

`.spectral.yaml` at repo root:

```yaml
extends: ["spectral:oas"]
rules:
  operation-description: error
  operation-operationId: error
  operation-tag-defined: error
```

### 13.5 Branch & commit conventions (already agreed — enforce them now)

- Branches: `feature/S1-A03-complaint-routes`, `fix/S1-A06-task-status-409` — **lead with the
  task ID** so the board and the branch line up.
- Conventional Commits: `feat:`, `fix:`, `chore:`, `docs:`, `test:`.
- Squash-merge only; one approving review required.
- Reference stories in the commit body: `Implements US-01, US-04.`

### 13.6 Ceremony cadence for the sprint push

Given 5 days left in Sprint 1, upgrade from twice-weekly to:
- **Daily 15-min standup** (async in a Slack/WhatsApp thread is fine): yesterday / today /
  blocked-on-whom.
- **Day-1 sync (today):** agree Option A/B/C, assign the 12 foundation tasks, confirm the two
  stub-first handoffs (`deps.py`, `conftest.py`).
- **Mid-sprint check (Jul 31):** if fewer than 14 of 21 endpoints are merged, cut scope to Option C
  rather than shipping 21 half-done endpoints.
- **Demo + retro (Aug 2).**

### 13.7 Housekeeping

- Delete the stray 95-byte `package-lock.json` at the repo root (untracked, not a real lockfile).
  The real one is `Frontend/package-lock.json`.
- Fix `Frontend/README.md` — it says React 18; `package.json` says React 19.2.7.
- Fix `Backend/README.md` — remove the "main is protected" claim or actually protect it (13.1).

---

## 14. TOOLING RECOMMENDATIONS

Based on what is already in this repo, not a generic list.

| Need | Recommendation | Why this, here |
|---|---|---|
| **API testing** | `pytest` + FastAPI `TestClient` (httpx-backed) | Already the declared stack; `httpx` is already listed in your dev group. TestClient runs the real ASGI app in-process — no server to start, no ports, works in CI unchanged. **Don't add `requests`.** |
| **Coverage** | `pytest-cov`, `--cov-fail-under=70` | Already in your dev group. The rubric gives 5 points for pytest coverage; a hard CI gate makes it non-negotiable. |
| **Test DB** | SQLite in-memory for unit + API tests; postgres:16 service for integration | Keeps the fast tests fast. Your CI already spins up postgres:16 — use it only for `tests/integration`. Avoid `JSONB`/`ARRAY` in models so both backends work. |
| **YAML validation** | **Spectral** (`@stoplight/spectral-cli`) in CI + Swagger Editor for eyeballing | Spectral is scriptable and catches missing descriptions/operationIds, which is exactly what the rubric marks. Swagger Editor is the manual double-check before submission. |
| **Contract drift** | Diff hand-written `openapi.yaml` against FastAPI's generated `/openapi.json` | FastAPI generates a spec from the code for free. If it diverges from your hand-written YAML, one of them is wrong — catch it in CI rather than in grading. |
| **CI** | GitHub Actions — extend the existing `backend-ci.yml`, add `frontend-ci.yml` + `openapi-lint.yml` | Already scaffolded and correctly configured with path filters and a postgres service. No reason to introduce anything else. |
| **Lint / format** | Ruff + Black (backend), oxlint (frontend) — all already configured | `.pre-commit-config.yaml` exists. Everyone should run `pre-commit install` once. |
| **Demo / manual QA** | Swagger UI at `/docs`, free from FastAPI | Postman/Newman is optional. Swagger UI is zero-setup and doubles as demo material for the Sprint review. Only add Newman if you want API tests in CI independent of pytest — you don't need both. |
| **Migrations** | Alembic, autogenerate then **hand-review** | Already configured in principle. Never edit an applied migration; always roll forward. |

**Explicitly not recommended:** adding Postman/Newman as a second test framework (duplicates
pytest for zero rubric gain), adding `requests` (TestClient covers it), or introducing a new
project-management tool (you already have two).

---

## 15. ASSUMPTIONS & OPEN DECISIONS

Items 1–3 change the API surface. **Decide them at the Day-1 sync**; the rest are safe defaults
already reflected in this plan.

### Needs a team decision

**1. Bulk pickup fees — contradiction between your own documents.**
`Backend/README.md` says *"BulkPickup — No fee / payment — service is municipality-run."*
`Frontend/src/context/BulkPickupContext.jsx` implements `calculateFee()` with load bands
(₹150 / ₹300 / ₹600 / ₹1000) and category surcharges (e-waste ₹200, construction debris ₹250,
scrap metal ₹100), storing a `fee` on every record. These cannot both be true.
**Assumed:** fees stay (the frontend already implements and displays them; removing them means
editing working UI). `POST /bulk-pickups` returns a computed `fee`. No payment processing —
fee is informational only.

**2. Roles for Health Officer (US-09) and Senior Authority (US-27).**
The frontend has exactly three roles: `citizen`, `crew`, `admin`. Milestone 1 names two more
personas. **Assumed:** add a fourth role `authority` for US-27, and treat Health Officer (US-09)
as an `admin` capability rather than a separate role. This adds one enum value and one
`ProtectedRoute` case — cheap. Alternative is mapping both onto `admin`, which is cheaper still
but makes US-09/US-27 hard to demo as distinct.

**3. Ward as an entity vs a string.**
`Backend/README.md` declares Ward first-class. The frontend uses free-text
(`"Indiranagar (Ward 12)"` in operational data, `"Ward 12"` in feed posts — already inconsistent
with itself). **Assumed:** a real `wards` table seeded with the 4 wards from
`collectionSchedule.js`, with `ward_id` FKs. The API returns both `ward_id` and a display `ward`
string so existing frontend components don't have to change in Sprint 1.

### Safe defaults (flagging, not blocking)

4. **US-28/29/30 as a `category` enum**, not three endpoints (see section 4 note).
5. **Notifications are in-app only** — DB rows polled by the client. No email/SMS; out of scope
   and needs credentials nobody has.
6. **Photo storage on local disk** under `UPLOAD_DIR`, served from a static mount. No S3/CDN.
   Validate mime type and cap at 5 MB.
7. **Duplicate detection stays advisory** — returns matches, never blocks submission. Same
   thresholds as the frontend (200 m / 0.6 / 0.35) read from config so they can't drift.
8. **Timestamps UTC**, ISO-8601 at the API boundary.
9. **Auth model:** citizens self-register; crew and admin accounts are provisioned by an admin.
   JWT access (30 min) + refresh (7 days), bcrypt hashing.
10. **Python 3.12, not 3.13.** `pyproject.toml` currently pins `>=3.13`, but the dev machine in
    this repo runs 3.12.3 and nothing in the stack needs 3.13. Recommend relaxing to `>=3.12`.
11. **Auth was entirely missing from your Sprint 1 CSV.** All 22 rows cover complaints and task
    assignment; none cover registration, login, or RBAC — yet every other endpoint depends on
    them. This plan adds 4 auth endpoints plus `deps.py` to Sprint 1. That is the single biggest
    gap between your existing CSV and a shippable sprint.
12. **Library swap from the README's stated stack:** use `PyJWT` + `bcrypt` directly instead of
    `python-jose` + `passlib`. `passlib` 1.7.4 is unmaintained and breaks against `bcrypt>=4.1`;
    `python-jose` has open CVEs. Same contract, fewer problems. Update `Backend/README.md` to match.
13. **Complaints currently reset on page reload** (in-memory context) while everything else
    persists to localStorage. Worth fixing before the Sprint 1 demo regardless of backend
    progress — a demo where complaints vanish on refresh reads badly.

---

*End of plan. Task IDs in sections 9 and 10 are stable — use them in branch names, commit
messages, and board cards.*
