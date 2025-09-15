#!/bin/bash
set -e

# Go to the app directory
cd /app

# Install backend dependencies
echo "--- Installing Backend Dependencies ---"
pip install -e .[dev]

# Install frontend dependencies
echo "--- Installing Frontend Dependencies ---"
(cd frontend && rm -rf node_modules package-lock.json && npm install)

# Start the backend server
echo "--- Starting Backend Server ---"
python meal_planner_app/main.py > backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend server started with PID: $BACKEND_PID"

# Start the frontend server
echo "--- Starting Frontend Server ---"
(cd frontend && npm run dev > ../frontend.log 2>&1) &
FRONTEND_PID=$!
echo "Frontend server started with PID: $FRONTEND_PID"

# Wait for servers to be ready
echo "--- Waiting for servers to start ---"
sleep 15

# Run the tests
echo "--- Running E2E Tests ---"
(cd frontend && npx playwright install && npm test)
TEST_EXIT_CODE=$?

# Stop the servers
echo "--- Stopping Servers ---"
kill $BACKEND_PID
kill $FRONTEND_PID

# Exit with the test exit code
exit $TEST_EXIT_CODE
