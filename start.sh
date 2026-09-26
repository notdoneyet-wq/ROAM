#!/bin/bash
# ROAM AI Travel Agent Startup Script

echo "=================================================="
echo "🧭 ROAM — AI Travel Agent"
echo "=================================================="

# Determine project directory
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$PROJECT_DIR"

# 1. Start Backend FastAPI Server
echo "Starting Backend Server on http://localhost:8000..."
cd "$PROJECT_DIR/backend"
source venv/bin/activate
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to spin up
sleep 2

# 2. Start Frontend Next.js Server
echo "Starting Frontend Server on http://localhost:3000..."
cd "$PROJECT_DIR/frontend"
npm run dev &
FRONTEND_PID=$!

echo "=================================================="
echo "✨ ROAM is live!"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   Docs:     http://localhost:8000/docs"
echo "=================================================="
echo "Press Ctrl+C to stop all servers."

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT INT TERM
wait
