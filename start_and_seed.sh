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

# Start the frontend dev server in the background
echo "Starting Vite frontend..."
cd /app/frontend
npm run dev -- --host 0.0.0.0 &
FRONTEND_PID=$!
cd /app

# Wait for the backend to be ready
echo "Waiting for backend to start..."
sleep 10

# Seed the database
echo "Seeding database..."
python -m meal_planner_app.seed_db

# Keep the container running by waiting for both processes
wait $BACKEND_PID $FRONTEND_PID
