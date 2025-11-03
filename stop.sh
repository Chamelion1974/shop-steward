#!/bin/bash
# Shop Steward Hub - Quick Stop Script (Linux/Mac)

echo "Stopping Shop Steward Hub servers..."

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Find and kill uvicorn (backend) processes
if pkill -f "uvicorn app.main:app"; then
    echo -e "${GREEN}✓ Backend server stopped${NC}"
else
    echo -e "${YELLOW}! No backend server found running${NC}"
fi

# Find and kill vite (frontend) processes
if pkill -f "vite"; then
    echo -e "${GREEN}✓ Frontend server stopped${NC}"
else
    echo -e "${YELLOW}! No frontend server found running${NC}"
fi

echo ""
echo -e "${CYAN}Shop Steward Hub has been stopped${NC}"
