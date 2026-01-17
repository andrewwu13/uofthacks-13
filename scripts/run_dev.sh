#!/bin/bash
# Development environment startup script

echo "Starting Gen UI development environment..."

# Start Redis
echo "Starting Redis..."
redis-server --daemonize yes

# Start MongoDB
echo "Starting MongoDB..."
mongod --fork --logpath /tmp/mongod.log

# Start backend
echo "Starting backend..."
cd backend
pip install -r requirements.txt > /dev/null 2>&1
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

# Start frontend
echo "Starting frontend..."
cd ../frontend
npm install > /dev/null 2>&1
npm run dev &
FRONTEND_PID=$!

echo ""
echo "Services started:"
echo "  Backend: http://localhost:8000"
echo "  Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop all services"

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT

wait
