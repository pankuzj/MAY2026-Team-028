# SmartSweep — Frontend

A React + Vite web app for reporting and tracking garbage/cleanliness complaints, with role-based views for Citizens, Cleanup Crew, and Supervisors/Admins.

## Tech Stack

* React 18
* React Router DOM (client-side routing)
* Vite (build tool / dev server)

## Project Structure

```
MAY2026-Team-028/
└── Frontend/
    ├── node_modules/     # installed dependencies (auto-generated, do not edit)
    ├── public/           # static assets
    ├── src/              # application source code
    │   ├── components/   # reusable UI components (Navbar, BottomNav, etc.)
    │   ├── context/       # React Context providers (Auth, Theme, Complaints)
    │   ├── pages/         # route-level pages (Login, Home, Report, etc.)
    │   ├── App.jsx
    │   └── main.jsx
    ├── index.html
    ├── package.json
    ├── package-lock.json
    ├── vite.config.js
    └── .oxlintrc.json
```

## Prerequisites

Before you begin, make sure you have installed:

* **Node.js** v18 or later — [download here](https://nodejs.org/)
* **npm** (comes bundled with Node.js)

Check your versions with:

```bash
node -v
npm -v
```

## Getting Started

### 1. Navigate to the `Frontend` folder

The project's `package.json` lives inside `Frontend/`, so all commands below must be run from there — not from the repo root.

```bash
cd Frontend
```

### 2. Install dependencies

```bash
npm install
```

This installs everything listed in `package.json`, including `react`, `react-dom`, and `react-router-dom`.

### 3. Start the development server

```bash
npm run dev
```

Vite will start a local dev server and print a URL in the terminal, typically:

```
http://localhost:5173
```

Open that URL in your browser to view the app. The dev server supports hot-reload — changes to files in `src/` will refresh automatically.

### 4. Build for production (optional)

```bash
npm run build
```

This generates an optimized production build in a `dist/` folder.

To preview the production build locally:

```bash
npm run preview
```

## Demo Login Credentials

The app currently uses hardcoded demo accounts (no backend yet):

| Role       | Username  | Password    |
|------------|-----------|-------------|
| Citizen    | citizen   | citizen123  |
| Cleanup Crew | crew    | crew123     |
| Admin / Supervisor | admin | admin123 |

## Troubleshooting

* **`Failed to resolve import "react-router-dom"`** → Run `npm install` inside the `Frontend` folder to make sure all dependencies are installed.
* **Blank page on load** → Open the browser console (F12) to check for errors; this usually means a missing export or import somewhere in `src/`.
* **Port already in use** → Vite will automatically try the next available port; check the terminal output for the actual URL.
* **Clean reinstall** (if things get stuck):
  ```bash
  rm -rf node_modules package-lock.json
  npm install
  ```

## Notes

This project is in early development. Complaint data is currently stored in-memory (via React Context) and resets on page reload — there is no backend/database integration yet.