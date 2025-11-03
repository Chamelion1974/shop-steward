#!/bin/bash
# Shop Steward Hub - Unified Startup Script (Linux/Mac)
# This script starts both backend and frontend servers

echo "================================================"
echo "   Starting Shop Steward Hub"
echo "================================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if virtual environment exists
if [ ! -f "env/bin/activate" ]; then
    echo -e "${RED}✗ Virtual environment not found!${NC}"
    echo -e "${RED}  Please run ./install.sh first${NC}"
    exit 1
fi

# Check if node_modules exists
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${RED}✗ Frontend dependencies not found!${NC}"
    echo -e "${RED}  Please run ./install.sh first${NC}"
    exit 1
fi

echo -e "${YELLOW}Starting backend server in background...${NC}"
./start-backend.sh &
BACKEND_PID=$!

sleep 2

echo -e "${YELLOW}Starting frontend server in background...${NC}"
./start-frontend.sh &
FRONTEND_PID=$!

echo ""
echo "================================================"
echo -e "${GREEN}   Shop Steward Hub is starting!${NC}"
echo "================================================"
echo ""
echo -e "${YELLOW}Backend PID: $BACKEND_PID${NC}"
echo -e "${YELLOW}Frontend PID: $FRONTEND_PID${NC}"
echo ""
echo -e "${YELLOW}Once both servers are ready, access the Hub at:${NC}"
echo -e "${CYAN}  Frontend: http://localhost:5173${NC}"
echo -e "${CYAN}  Backend:  http://localhost:8000${NC}"
echo -e "${CYAN}  API Docs: http://localhost:8000/api/docs${NC}"
echo ""
echo -e "${YELLOW}Default credentials:${NC}"
echo -e "${CYAN}  Username: admin${NC}"
echo -e "${CYAN}  Password: admin123${NC}"
echo ""
echo -e "${YELLOW}To stop the servers, press Ctrl+C${NC}"
echo ""

# Wait for Ctrl+C
trap "echo ''; echo 'Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT

# Keep script running
wait
