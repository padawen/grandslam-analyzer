#!/bin/bash

# Configuration
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

echo "Starting Grand Slam Analyzer..."

# Start Backend
echo "Starting Backend (FastAPI)..."
cd "$BACKEND_DIR"
# Check if venv exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi
# Start in background
python3 main.py &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Start Frontend
echo "Starting Frontend (Vite)..."
cd "$FRONTEND_DIR"
# Assuming npm is installed
npm run dev &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

# Handle shutdown
trap "kill $BACKEND_PID $FRONTEND_PID; exit" SIGINT SIGTERM

echo "Both services are starting. Press Ctrl+C to stop."
wait
