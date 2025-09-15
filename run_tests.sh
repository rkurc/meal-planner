#!/bin/bash
set -e

# Go to the app directory
cd /app

# Check for Node and npm
echo "--- Checking Frontend Environment ---"
if ! command -v node &> /dev/null || ! command -v npm &> /dev/null; then
    echo "Node.js and/or npm could not be found. Please install them to run the frontend tests."
    exit 1
fi

# Install frontend dependencies
echo "--- Installing Frontend Dependencies ---"
(cd frontend && npm install)

# Remove old database file
echo "--- Removing Old Database File ---"
rm -f instance/meal_planner.db

# Create database tables
echo "--- Creating Database Tables ---"
python -m meal_planner_app.init_db

# Seed the database
echo "--- Seeding Database ---"
python -m meal_planner_app.seed_db

# Start the backend server
echo "--- Starting Backend Server ---"
python run.py > backend.log 2>&1 &
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
(cd frontend && npm test)
TEST_EXIT_CODE=$?

# Stop the servers
echo "--- Stopping Servers ---"
kill $BACKEND_PID
kill $FRONTEND_PID

# Exit with the test exit code
exit $TEST_EXIT_CODE
