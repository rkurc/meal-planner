#!/bin/bash
set -e

# NOTE: This script is for DEVELOPMENT only.
# It starts Flask (debug) + Vite dev server (npm run dev) then seeds data.
# The production image (built from root Dockerfile) does NOT use this:
#   - no Node/npm at runtime
#   - uses gunicorn directly
#   - serves React SPA from /ui/
# For dev with full HMR use the devcontainer or run this on host with Node.

# Start the backend in the background
echo "Starting Flask backend..."
python -m meal_planner_app.main &
BACKEND_PID=$!

# Start the frontend dev server in the background (only if npm is available).
# In prod-style images without Node (or lean prod), we just serve the prebuilt
# React assets via Flask at /ui/.
echo "Starting Vite frontend..."
if command -v npm >/dev/null 2>&1; then
  cd /app/frontend
  npm run dev -- --host 0.0.0.0 &
  FRONTEND_PID=$!
  cd /app
else
  echo "npm not found - skipping Vite (using static assets at /ui/)"
  FRONTEND_PID=""
fi

# Wait for the backend to be ready
echo "Waiting for backend to start..."
sleep 10

# Migrate from legacy data if present.
# Preferred: place a clean UTF-8 recipes.csv (exported from Base via Calc).
# Fallback: przepisy_tmp.odb (heuristic).
if [ -f /app/legacy/recipes.csv ] || [ -f /app/legacy/przepisy.csv ] || [ -f /app/legacy/przepisy_tmp.odb ]; then
  echo "Legacy data found - running migration (prefers CSV if present)..."
  python -m meal_planner_app.migrate_legacy || python -m meal_planner_app.seed_db
else
  echo "Seeding database with defaults..."
  python -m meal_planner_app.seed_db
fi

# Keep the container running by waiting for the backend (and frontend if we started it)
if [ -n "$FRONTEND_PID" ]; then
  wait $BACKEND_PID $FRONTEND_PID
else
  wait $BACKEND_PID
fi
