#!/bin/bash
set -e

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
