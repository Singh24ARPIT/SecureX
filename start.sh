#!/usr/bin/env bash
set -e

echo "======================================================="
echo "Starting SentinelAI – Autonomous Real-Time DAST Engine"
echo "VOYAGEHACK 4.0 | TBO Security Hackathon 2026"
echo "======================================================="

# Ensure virtualenv exists
if [ ! -d "venv" ]; then
    echo "Creating virtualenv..."
    python3 -m venv venv
    ./venv/bin/pip install -r backend/requirements.txt
fi

# Ensure frontend node_modules exist
if [ ! -d "frontend/node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install --prefix frontend
fi

echo "Starting FastAPI Backend on http://127.0.0.1:8000..."
export PYTHONPATH=backend
./venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload &
BACKEND_PID=$!

echo "Starting React Vite Frontend on http://127.0.0.1:5173..."
npm run dev --prefix frontend &
FRONTEND_PID=$!

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT

echo ""
echo "======================================================="
echo "SentinelAI Platform is LIVE!"
echo "Backend Docs:  http://127.0.0.1:8000/docs"
echo "Frontend UI:   http://127.0.0.1:5173"
echo "Default Admin: admin / SentinelAdmin2026!"
echo "Press Ctrl+C to terminate services."
echo "======================================================="

wait

