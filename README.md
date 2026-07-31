# SmartSweep

A civic-tech platform for reporting, tracking, and resolving municipal waste and sanitation issues — connecting citizens, collection crews, and municipal administrators in one system.

---

## Overview

SmartSweep gives residents a direct way to report waste-management problems — overflowing bins, missed pickups, illegal dumping, bulk waste — and gives municipal staff the tools to triage, assign, and resolve them. It's built around four roles, each with a purpose-built view of the same underlying data:

- **Citizens** report complaints, request bulk pickups, and track resolution status.
- **Crew** members receive task assignments and update job status in the field.
- **Admins** manage workers, equipment, and vehicles, and oversee the complaint pipeline.
- **Authority** users get oversight and reporting views for accountability and transparency.

The platform also includes a public transparency feed, a duplicate-complaint detector (so the same pothole-adjacent trash pile doesn't get reported five times), and a ward-based collection schedule that residents can check without calling anyone.

## Key Features

- **Complaint lifecycle management** — submit, track, and resolve complaints with status transitions (`Pending → In Progress → Resolved`, with `Cancelled` as an exit path).
- **Bulk pickup requests** — scheduled pickups with automatic fee calculation based on load size and waste category.
- **Task assignment & crew workflows** — admins assign work to crew members; crew update task and equipment/vehicle status in real time.
- **Duplicate detection** — new complaints are checked against nearby existing ones using location proximity and text similarity, so duplicates are flagged (not blocked) for review.
- **Ward-based collection schedules** — recurring pickup calendars per ward, computed rather than hardcoded, with support for one-off exceptions.
- **Role-based access control** — every route and view is gated by role (`citizen`, `crew`, `admin`, `authority`).
- **Transparency feed & reporting** — public-facing posts and reports for community accountability.
- **Geolocation-assisted reporting** — complaints can be submitted with an auto-detected location, reverse-geocoded into a readable address.

## Tech Stack

### Frontend
| Layer | Technology |
|---|---|
| Framework | React |
| Routing | React Router, with role-gated protected routes |
| Charts | Recharts |
| Build tool | Vite |
| Linting | oxlint |
| State/persistence | React Context, with `localStorage` for durable data |

### Backend
| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Database | PostgreSQL |
| ORM & migrations | SQLAlchemy + Alembic |
| Auth | JWT (access + refresh tokens) via PyJWT, password hashing via bcrypt |
| Package management | uv |
| API docs | Auto-generated OpenAPI/Swagger UI (`/docs`), cross-checked against a hand-written spec |
| Testing | pytest, with `pytest-cov` for coverage |
| Containerization | Docker Compose (Postgres service) |
| CI | GitHub Actions |

### Integrations
| What | Used for |
|---|---|
| Browser Geolocation API | Auto-detecting a citizen's location on complaint submission |
| Nominatim (OpenStreetMap) | Reverse geocoding coordinates into a human-readable address |
| Claude API | Suggesting hazard type and severity from complaint text/photos |

## Project Structure

```
SmartSweep/
├── Frontend/
│   ├── src/
│   │   ├── context/        # AuthContext, ComplaintsContext, BulkPickupContext, OperationalContext
│   │   ├── components/     # Shared UI components
│   │   ├── pages/           # Route-level views, gated by ProtectedRoute
│   │   └── utils/           # duplicateDetection.js, collectionSchedule.js
│   ├── package.json
│   └── README.md
├── Backend/
│   ├── app/
│   │   ├── api/             # Route handlers
│   │   ├── services/        # Business logic
│   │   ├── repositories/    # Data access layer
│   │   └── models/          # SQLAlchemy models & Pydantic schemas
│   ├── alembic/              # Database migrations
│   ├── docker-compose.yml    # Local Postgres service
│   ├── .env.example
│   ├── pyproject.toml
│   └── README.md
├── docs/
│   └── openapi.yaml          # Hand-written API contract
└── .github/
    └── workflows/            # CI pipelines
```

The four React Contexts on the frontend (`Auth`, `Complaints`, `BulkPickup`, `Operational`) function as the de-facto API contract — they define the exact shape of data the backend needs to serve.

## Getting Started

### Prerequisites
- Node.js and npm (frontend)
- Python 3.12+ and [uv](https://github.com/astral-sh/uv) (backend)
- Docker (for local PostgreSQL)

### Frontend

```bash
cd Frontend
npm install
npm run dev
```

### Backend

```bash
cd Backend
cp .env.example .env       # fill in the required values
docker compose up -d       # starts PostgreSQL
uv sync --all-extras
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

Once running, interactive API documentation is available at `http://localhost:8000/docs`.

### Running Tests

```bash
# Backend
cd Backend
uv run pytest --cov=app --cov-report=term-missing

# Frontend
cd Frontend
npm run lint
```

## Status

The frontend is a fully working React application with role-based routing, mock authentication, and local persistence for most data. The backend currently provides the architectural scaffold — folder structure, environment configuration, database service, and CI pipeline — with the API implementation itself in progress. The frontend's Context layer is designed so its data-fetching functions can be swapped from local state to real API calls with minimal changes to the UI components that consume them.

## License

Add your license of choice here (e.g. MIT, Apache 2.0).
