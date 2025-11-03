#!/bin/bash
# Shop Steward Hub - Backend Startup Script (Linux/Mac)

echo "================================================"
echo "   Shop Steward Hub - Backend Server"
echo "================================================"
echo ""

# Colors
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source env/bin/activate

# Change to backend directory
cd backend

echo -e "${YELLOW}Starting FastAPI server...${NC}"
echo ""

# Start uvicorn server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
