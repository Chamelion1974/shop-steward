#!/bin/bash
# Shop Steward Hub - Linux/Mac Installation Script
# This script sets up the Shop Steward Hub on Linux and macOS systems

echo "================================================"
echo "   Shop Steward Hub - Installation Script"
echo "================================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check if Python is installed
echo -e "${YELLOW}Checking Python installation...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓ Found: $PYTHON_VERSION${NC}"
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version)
    echo -e "${GREEN}✓ Found: $PYTHON_VERSION${NC}"
    PYTHON_CMD=python
else
    echo -e "${RED}✗ Python not found!${NC}"
    echo -e "${RED}Please install Python 3.11 or higher${NC}"
    exit 1
fi

# Check if Node.js is installed
echo -e "${YELLOW}Checking Node.js installation...${NC}"
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓ Found Node.js: $NODE_VERSION${NC}"
else
    echo -e "${RED}✗ Node.js not found!${NC}"
    echo -e "${RED}Please install Node.js 18 or higher from https://nodejs.org/${NC}"
    exit 1
fi

# Check if npm is installed
echo -e "${YELLOW}Checking npm installation...${NC}"
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    echo -e "${GREEN}✓ Found npm: $NPM_VERSION${NC}"
else
    echo -e "${RED}✗ npm not found!${NC}"
    exit 1
fi

echo ""
echo "================================================"
echo "   Setting up Backend (Python)"
echo "================================================"

# Create Python virtual environment
echo -e "${YELLOW}Creating Python virtual environment...${NC}"
if [ -d "env" ]; then
    echo -e "${GREEN}Virtual environment already exists, skipping...${NC}"
else
    $PYTHON_CMD -m venv env
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Virtual environment created${NC}"
    else
        echo -e "${RED}✗ Failed to create virtual environment${NC}"
        exit 1
    fi
fi

# Activate virtual environment and install backend dependencies
echo -e "${YELLOW}Installing backend dependencies...${NC}"
source env/bin/activate
pip install --upgrade pip
cd backend
pip install -r requirements.txt
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Backend dependencies installed${NC}"
else
    echo -e "${RED}✗ Failed to install backend dependencies${NC}"
    cd ..
    exit 1
fi
cd ..

echo ""
echo "================================================"
echo "   Setting up Frontend (Node.js)"
echo "================================================"

# Install frontend dependencies
echo -e "${YELLOW}Installing frontend dependencies...${NC}"
cd frontend
npm install
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
else
    echo -e "${RED}✗ Failed to install frontend dependencies${NC}"
    cd ..
    exit 1
fi
cd ..

echo ""
echo "================================================"
echo "   Configuration"
echo "================================================"

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
    echo -e "${YELLOW}Creating default .env file...${NC}"
    if [ -f "backend/.env.example" ]; then
        cp backend/.env.example backend/.env
        echo -e "${GREEN}✓ .env file created${NC}"
        echo -e "${CYAN}  Note: Edit backend/.env to customize settings${NC}"
    else
        echo -e "${YELLOW}! No .env.example found, continuing without .env...${NC}"
    fi
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

# Create necessary directories
echo -e "${YELLOW}Creating upload and module directories...${NC}"
mkdir -p backend/uploads
mkdir -p backend/modules
mkdir -p uploads
mkdir -p modules
echo -e "${GREEN}✓ Directories created${NC}"

# Make startup scripts executable
echo -e "${YELLOW}Making startup scripts executable...${NC}"
chmod +x start.sh 2>/dev/null || true
chmod +x start-backend.sh 2>/dev/null || true
chmod +x start-frontend.sh 2>/dev/null || true
echo -e "${GREEN}✓ Startup scripts are executable${NC}"

echo ""
echo "================================================"
echo -e "${GREEN}   Installation Complete!${NC}"
echo "================================================"
echo ""
echo -e "${YELLOW}To start the Shop Steward Hub:${NC}"
echo -e "${CYAN}  1. Run: ./start.sh${NC}"
echo -e "     (This will start both backend and frontend servers)"
echo ""
echo -e "${YELLOW}Or start them separately:${NC}"
echo -e "${CYAN}  Backend:  ./start-backend.sh${NC}"
echo -e "${CYAN}  Frontend: ./start-frontend.sh${NC}"
echo ""
echo -e "${YELLOW}Default admin credentials:${NC}"
echo -e "${CYAN}  Username: admin${NC}"
echo -e "${CYAN}  Password: admin123${NC}"
echo -e "${RED}  ⚠️  Change these immediately after first login!${NC}"
echo ""
echo -e "${YELLOW}Access the Hub at:${NC}"
echo -e "${CYAN}  Frontend: http://localhost:5173${NC}"
echo -e "${CYAN}  Backend:  http://localhost:8000${NC}"
echo -e "${CYAN}  API Docs: http://localhost:8000/api/docs${NC}"
echo ""
