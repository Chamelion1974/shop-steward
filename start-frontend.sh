#!/bin/bash
# Shop Steward Hub - Frontend Startup Script (Linux/Mac)

echo "================================================"
echo "   Shop Steward Hub - Frontend Server"
echo "================================================"
echo ""

# Colors
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Change to frontend directory
cd frontend

echo -e "${YELLOW}Starting Vite development server...${NC}"
echo ""

# Start Vite dev server
npm run dev
