# SmartSweep

A modern civic-tech platform for reporting, dispatching, and resolving municipal waste and sanitation issues — bridging citizens, collection crews, and ward administrators in a unified system.

[![Backend CI](https://github.com/pankuzj/MAY2026-Team-028/actions/workflows/backend-ci.yml/badge.svg)](https://github.com/pankuzj/MAY2026-Team-028/actions/workflows/backend-ci.yml)
[![Frontend CI](https://github.com/pankuzj/MAY2026-Team-028/actions/workflows/frontend-ci.yml/badge.svg)](https://github.com/pankuzj/MAY2026-Team-028/actions/workflows/frontend-ci.yml)
[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](https://github.com/pankuzj/MAY2026-Team-028)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12%2B-blue?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61dafb?logo=react&logoColor=black)](https://react.dev)

---

🔗 **Live Deployment:** [smartsweep-frontend.vercel.app](https://smartsweep-frontend.vercel.app/)

---

## Overview

SmartSweep modernizes municipal waste operations by providing an end-to-end management ecosystem for sanitation complaints, bulk pickups, and resource allocation. It empowers citizens to report street waste and illegal dumping with automatic geolocation and AI hazard classification, while giving municipal crews and supervisors real-time tools to dispatch workforce, assign fleet vehicles, and track ticket resolutions. The platform ensures civic transparency through public accountability feeds and data-driven ward performance metrics.

---

## Features

- **Citizen Issue Reporting & Auto-Geocoding** — Submit complaints with attached photos, auto-detected GPS coordinates, and reverse-geocoded street addresses via OpenStreetMap Nominatim.
- **AI Hazard & Severity Classification** — Claude API integration automatically assesses waste descriptions and images to suggest hazard categories and urgency levels.
- **Proactive Duplicate Detection** — Geospatial radius (Haversine) and text-similarity matching flag potential duplicate complaints prior to submission to prevent duplicate ticket triage.
- **Role-Based Task Dispatch & Lifecycle** — End-to-end workflow transitions (`Pending → In Progress → Resolved / Cancelled`) with full audit history.
- **Workforce, Vehicle & Equipment Management** — Ward supervisors assign available field crews, sanitation vehicles, and equipment inventory to active complaints and pickup tasks.
- **Crew Field Operations** — Field-ready interface for cleanup workers to view assigned routes, inspect hazard details, and update job status with resolution evidence.
- **Bulk Waste Pickup Scheduling** — Citizens can request scheduled pickups for oversized or hazardous items with volume specifications and category handling.
- **Ward-Based Collection Timetables** — Computed recurring collection schedules and exception calendars per ward, accessible to residents on demand.
- **Public Transparency Feed & Civic Analytics** — Community feed displaying resolved issues with before/after photos and applause, backed by supervisor trend analytics powered by Recharts.

---

## Tech Stack

### Frontend
- **Framework & Runtime:** React 19, Vite
- **Routing:** React Router v7 (with role-based route guards)
- **Data Visualization:** Recharts
- **Linting:** Oxlint
- **Styling:** CSS Design System with dark/light mode support

### Backend
- **Framework:** FastAPI (Python 3.12+)
- **ASGI Server:** Uvicorn
- **Database & ORM:** PostgreSQL 16, Psycopg 3, SQLAlchemy 2.0
- **Database Migrations:** Alembic
- **Validation & Settings:** Pydantic v2, Pydantic-Settings
- **Authentication:** JWT (PyJWT) with bcrypt password hashing & RBAC
- **Dependency Management:** `uv`
- **Testing & Quality:** Pytest, pytest-cov, Ruff, Black

### Integrations & Infrastructure
- **AI / LLM:** Anthropic Claude API (Hazard and severity classification)
- **Geolocation:** OpenStreetMap Nominatim API & HTML5 Geolocation API
- **Containerization:** Docker & Docker Compose
- **Continuous Integration:** GitHub Actions

---

## Installation

### Prerequisites
- [Node.js](https://nodejs.org/) (v18+) & `npm`
- [Python](https://www.python.org/) (v3.12+) and [`uv`](https://github.com/astral-sh/uv)
- [Docker](https://www.docker.com/) & Docker Compose (for PostgreSQL)

---

### 1. Clone the Repository

```bash
git clone git@github.com:pankuzj/MAY2026-Team-028.git
cd MAY2026-Team-028
```

---

### 2. Backend Setup

#### Option A: Docker Compose (Quickest)

Runs both PostgreSQL and the FastAPI service in isolated containers:

```bash
cd Backend
docker compose up --build -d
```

API docs will be available at `http://localhost:8000/docs`.

#### Option B: Local Setup with `uv` (Recommended for Development)

```bash
cd Backend

# 1. Start local PostgreSQL database container
docker compose up -d db

# 2. Configure environment variables
cp .env.example .env

# 3. Install Python dependencies
uv sync --all-extras

# 4. Apply database migrations
uv run alembic upgrade head

# 5. Start the FastAPI development server
uv run uvicorn app.main:app --reload --port 8000
```

---

### 3. Frontend Setup

In a new terminal window:

```bash
cd Frontend

# 1. Install dependencies
npm install

# 2. Start the Vite development server
npm run dev
```

The web application will be accessible at `http://localhost:5173`.

---

## Usage

### Demo Accounts

The database seeds demo accounts across all supported roles on first startup:

| Role | Email | Password | Access Level |
|---|---|---|---|
| **Citizen** | `citizen@smartsweep.gov` | `citizen123` | Submit complaints, schedule bulk pickup, view personal history & public feed |
| **Citizen (Anita)** | `anita@smartsweep.gov` | `anita123` | Citizen account in Ward 2 |
| **Citizen (Mohammed)** | `mohammed@smartsweep.gov` | `mohammed123` | Citizen account in Ward 3 |
| **Cleanup Crew** | `crew@smartsweep.gov` | `crew123` | View assigned routes/tasks, update task progress, log equipment |
| **Ward Supervisor / Admin** | `admin@smartsweep.gov` | `admin123` | Dispatch workforce, assign fleet vehicles, manage inventory & review analytics |

> **Note:** Citizens and Crew members can also self-register at `/register`. Administrator accounts are provisioned exclusively via database seeding or admin invitation.

---

### Running Tests and Linting

#### Backend Tests & Coverage

```bash
cd Backend
uv run pytest --cov=app --cov-report=term-missing
uv run ruff check .
uv run black --check .
```

#### Frontend Linting & Build Verification

```bash
cd Frontend
npm run lint
npm run build
```

---

## Environment Variables

Configuration is managed via `Backend/.env`. The table below outlines all available settings:

| Variable | Type | Default / Example | Description | Required |
|---|---|---|---|---|
| `ENV` | `string` | `dev` | Application environment (`dev`, `test`, `prod`) | Yes |
| `LOG_LEVEL` | `string` | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) | No |
| `DATABASE_URL` | `string` | `postgresql+psycopg://smartsweep:smartsweep@localhost:5432/smartsweep` | PostgreSQL connection URI | Yes |
| `DB_ECHO` | `boolean` | `false` | Enable verbose SQLAlchemy query logging | No |
| `JWT_SECRET_KEY` | `string` | `change-me` | Secret key for signing JWT tokens | Yes |
| `JWT_ALGORITHM` | `string` | `HS256` | JWT cryptographic algorithm | No |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `integer` | `30` | Access token lifespan in minutes | No |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | `integer` | `7` | Refresh token lifespan in days | No |
| `CORS_ORIGINS` | `string` | `http://localhost:5173` | Comma-separated list of allowed frontend origins | Yes |
| `UPLOAD_DIR` | `string` | `./uploads` | Local directory for storing complaint images | No |
| `UPLOAD_MAX_BYTES` | `integer` | `5242880` | Maximum file upload size in bytes (5 MB) | No |
| `DUPLICATE_RADIUS_METERS` | `float` | `200` | Proximity radius in meters for duplicate checks | No |
| `DUPLICATE_TEXT_SIMILARITY_THRESHOLD` | `float` | `0.6` | Text similarity cutoff for duplicate suggestions | No |
| `DUPLICATE_SCORE_THRESHOLD` | `float` | `0.35` | Combined confidence threshold for duplicate flagging | No |
| `ANTHROPIC_API_KEY` | `string` | `""` | Claude API key for AI hazard classification | No |
| `NOMINATIM_BASE_URL` | `string` | `https://nominatim.openstreetmap.org` | OpenStreetMap reverse-geocoding endpoint | No |
| `NOMINATIM_USER_AGENT` | `string` | `SmartSweep/0.1` | User-Agent header for Nominatim API requests | No |

---

## Project Structure

```
MAY2026-Team-028/
├── .github/
│   └── workflows/              # GitHub Actions CI pipelines (Backend, Frontend, OpenAPI)
├── Backend/
│   ├── alembic/                # Database schema migrations
│   ├── app/
│   │   ├── api/                # HTTP layer & dependencies (deps.py, v1/routes)
│   │   ├── core/               # App configuration, security (JWT/bcrypt), exceptions
│   │   ├── db/                 # Database engine, session lifecycle, seed data
│   │   ├── models/             # SQLAlchemy ORM domain models
│   │   ├── repositories/       # Data persistence & database query layer
│   │   ├── schemas/            # Pydantic v2 request/response schemas
│   │   ├── services/           # Core business logic & state machine engines
│   │   └── utils/              # Pure helpers (haversine formula, text similarity)
│   ├── tests/                  # Unit, integration, and API test suites
│   ├── docker-compose.yml      # Local container orchestration
│   ├── Dockerfile              # Backend container definition
│   ├── pyproject.toml          # uv packaging configuration and tool settings
│   └── .env.example            # Environment configuration template
├── Frontend/
│   ├── src/
│   │   ├── components/         # Shared UI components (Navbar, ProtectedRoute, etc.)
│   │   ├── context/            # React Contexts (AuthContext, ComplaintsContext, etc.)
│   │   ├── pages/              # Route-level views (ReportComplaint, SupervisorDashboard, etc.)
│   │   └── utils/              # API clients, duplicate detection, schedule computation
│   ├── package.json            # Node.js dependencies and scripts
│   └── vite.config.js          # Vite build configuration
└── docs/                       # Project documentation and specifications
```

---

## Roadmap

- [x] **Milestone 1:** Core architecture, domain data models, JWT authentication, and wireframe views.
- [x] **Milestone 2:** End-to-end complaint workflow, duplicate detection, bulk pickup scheduling, and supervisor analytics.
- [x] **Sprint 2:** Claude-powered hazard analysis, reverse geocoding integration, and live Vercel deployment.
- [ ] **Real-Time GPS Crew Tracking:** Dynamic map view tracking sanitation vehicles and active routes.
- [ ] **Citizen Push Notifications:** Automated SMS/browser notifications on complaint status updates.
- [ ] **Offline Crew Support:** Progressive Web App (PWA) caching for low-connectivity field operations.

---

## Contributing

Contributions are welcome. Please follow these steps:

1. Create a descriptive feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Ensure code formatting and tests pass:
   ```bash
   # Backend
   cd Backend && uv run ruff check . && uv run pytest

   # Frontend
   cd ../Frontend && npm run lint
   ```
3. Commit with clear, conventional messages:
   ```bash
   git commit -m "feat(complaints): add export to csv functionality"
   ```
4. Open a Pull Request against the `main` branch with a summary of your changes.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Contact & Links

- **Live Application:** [https://smartsweep-frontend.vercel.app/](https://smartsweep-frontend.vercel.app/)
- **GitHub Repository:** [https://github.com/pankuzj/MAY2026-Team-028](https://github.com/pankuzj/MAY2026-Team-028)
