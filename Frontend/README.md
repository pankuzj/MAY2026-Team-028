# SmartSweep — Frontend

**SmartSweep** is a civic services platform for reporting and tracking garbage/waste-collection issues. This repository contains the **frontend-only** build (Milestone 2 deliverable) — a React + Vite web app with dedicated, role-based views for **Citizens**, **Cleanup Crew**, and **Ward Supervisors / Admins**.

> This is the frontend layer only. It is not yet wired up to a backend/database — complaint data lives in-memory (React Context) and resets on page reload. Backend API integration begins in Sprint 1 (Milestone 3).

---

## Tech Stack

| Layer | Technology |
|---|---|
| UI Library | React 18 |
| Routing | React Router DOM |
| Build tool / dev server | Vite |
| Styling | CSS (dark/light theme toggle built in) |

---

## Project Structure

```
MAY2026-Team-028/
└── Frontend/
    ├── node_modules/      # installed dependencies (auto-generated, do not edit)
    ├── public/            # static assets
    ├── src/
    │   ├── components/    # reusable UI components (Navbar, BottomNav, etc.)
    │   ├── context/        # React Context providers (Auth, Theme, Complaints)
    │   ├── pages/          # route-level pages (Login, Report Issue, My Complaints,
    │   │                    #   Public Feed, Assigned Tasks, Vehicles, Bulk Pickup,
    │   │                    #   Supervisor Dashboard, Reports & Trends, etc.)
    │   ├── App.jsx
    │   └── main.jsx
    ├── index.html
    ├── package.json
    ├── package-lock.json
    ├── vite.config.js
    └── .oxlintrc.json
```

---

## Prerequisites

Before you begin, make sure you have installed:

* **Node.js** v18 or later — [download here](https://nodejs.org/)
* **npm** (comes bundled with Node.js)

Check your versions with:

```bash
node -v
npm -v
```

---

## Installation & Run Instructions

### On Ubuntu / macOS

```bash
# 1. Navigate to the Frontend folder
#    (package.json lives inside Frontend/, not the repo root)
cd MAY2026-Team-028/Frontend

# 2. Install dependencies
npm install

# 3. Start the development server
npm run dev
```

### On Windows

```powershell
# 1. Clone the repository
git clone <repository-url>

# 2. Navigate to the Frontend folder
cd MAY2026-Team-028\Frontend

# 3. Install dependencies
npm install

# 4. Start the development server
npm run dev
```

Vite will start a local dev server and print a URL in the terminal, typically:

```
http://localhost:5173
```

Open that URL in your browser to view the app. The dev server supports hot-reload — changes to files in `src/` refresh automatically.

### Build for production (optional)

```bash
npm run build      # generates an optimized build in dist/
npm run preview    # preview the production build locally
```

---

## Demo Login Credentials

The app currently uses hardcoded demo accounts (no backend yet):

| Role | Username | Password |
|---|---|---|
| Citizen 1 (Sagnik) | `citizen` | `citizen123` |
| Citizen 2 (Anita) | `anita` | `anita123` |
| Citizen 3 (Mohammed) | `mohammed` | `mohammed123` |
| Cleanup Crew | `crew` | `crew123` |
| Ward Supervisor / Admin | `admin` | `admin123` |

---

## What's Implemented (Milestone 2)

- **Citizen:** report a garbage issue (location, description, hazard classification, photo upload), track "My Complaints," schedule a bulk waste pickup, and view the Public Transparency & Impact Feed.
- **Cleanup Crew:** view assigned tasks with hazard info, manage vehicle/fleet assignment, and manage bulk pickups.
- **Ward Supervisor / Admin:** supervisor dashboard for all complaints, fleet & vehicle assignment, bulk pickup management, and Reports & Trends analytics.
- All pages are linked and navigable across roles, with a dark/light theme toggle.

---

## Troubleshooting

* **`Failed to resolve import "react-router-dom"`** → Run `npm install` inside the `Frontend` folder to make sure all dependencies are installed.
* **Blank page on load** → Open the browser console (F12) to check for errors; this usually means a missing export or import somewhere in `src/`.
* **Port already in use** → Vite automatically tries the next available port; check the terminal output for the actual URL.
* **Clean reinstall** (if things get stuck):
  ```bash
  rm -rf node_modules package-lock.json
  npm install
  ```

---

## Notes

This project is in early development. Complaint data is currently stored in-memory (via React Context) and resets on page reload — there is no backend/database integration yet. Backend API work (Complaint, Task Assignment, Verification, Reports, etc.) begins in Sprint 1 / Milestone 3.
