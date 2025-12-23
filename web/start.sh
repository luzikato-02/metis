#!/bin/bash

# Start script for the Data Cleaning Web Application
# This script starts both the Flask backend and React frontend

echo "🚀 Starting Data Cleaning Web Application..."

# Check if we're in the right directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📦 Installing dependencies...${NC}"

# Install Python dependencies if not already installed
pip install -q -r backend/requirements.txt 2>/dev/null

# Install Node dependencies if not already installed
if [ ! -d "frontend/node_modules" ]; then
    echo "Installing frontend dependencies..."
    cd frontend && npm install && cd ..
fi

echo -e "${GREEN}✅ Dependencies installed${NC}"

# Create trap to kill background processes on exit
trap 'kill $(jobs -p) 2>/dev/null' EXIT

# Start Flask backend
echo -e "${BLUE}🐍 Starting Flask backend on http://localhost:5000...${NC}"
cd backend
python app.py &
FLASK_PID=$!
cd ..

# Wait for Flask to start
sleep 2

# Start React frontend
echo -e "${BLUE}⚛️  Starting React frontend on http://localhost:5173...${NC}"
cd frontend
npm run dev &
VITE_PID=$!
cd ..

echo ""
echo -e "${GREEN}=============================================${NC}"
echo -e "${GREEN}🎉 Application is running!${NC}"
echo -e "${GREEN}=============================================${NC}"
echo ""
echo -e "   ${BLUE}Frontend:${NC} http://localhost:5173"
echo -e "   ${BLUE}API:${NC}      http://localhost:5000/api"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for processes
wait
