# Shop Steward Hub - Installation & Startup Scripts

This directory contains easy-to-use installation and startup scripts for all platforms.

## 📦 Installation Scripts

Choose the script for your operating system:

### Windows

**Option 1: Double-click (Easiest)**
- Double-click `install.bat` in File Explorer

**Option 2: PowerShell**
```powershell
.\install.ps1
```

**Option 3: Command Prompt**
```cmd
install.bat
```

### Linux / Mac

```bash
chmod +x install.sh
./install.sh
```

## 🚀 Startup Scripts

After installation, start the Hub:

### Windows

**Option 1: Double-click**
- Double-click `start.bat` in File Explorer

**Option 2: PowerShell**
```powershell
.\start.ps1
```

**Option 3: Command Prompt**
```cmd
start.bat
```

### Linux / Mac

```bash
./start.sh
```

## 🛑 Stop Scripts

To stop all servers:

### Windows

**Option 1: Double-click**
- Double-click `stop.bat` in File Explorer

**Option 2: PowerShell**
```powershell
.\stop.ps1
```

**Option 3: Command Prompt**
```cmd
stop.bat
```

Or press `Ctrl+C` in each server window.

### Linux / Mac

```bash
./stop.sh
```

Or press `Ctrl+C` in the terminal.

## 📚 Documentation

- **[INSTALL.md](INSTALL.md)** - Detailed installation guide with troubleshooting
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Quick command reference
- **[README.md](README.md)** - Complete feature documentation
- **[WORKFLOW.md](WORKFLOW.md)** - Workflow management documentation

## 🎯 Quick Start

1. **Install**: Run `install.bat` (Windows) or `./install.sh` (Linux/Mac)
2. **Start**: Run `start.bat` (Windows) or `./start.sh` (Linux/Mac)
3. **Access**: Open http://localhost:5173
4. **Login**: Username: `admin`, Password: `admin123`
5. **Change Password**: Go to Settings → Password

## 📁 Script Files

| File | Platform | Purpose |
|------|----------|---------|
| `install.bat` | Windows | Easy installer (runs install.ps1) |
| `install.ps1` | Windows | PowerShell installation script |
| `install.sh` | Linux/Mac | Bash installation script |
| `start.bat` | Windows | Easy startup (runs start.ps1) |
| `start.ps1` | Windows | PowerShell startup (both servers) |
| `start.sh` | Linux/Mac | Bash startup (both servers) |
| `start-backend.ps1` | Windows | Backend only |
| `start-backend.sh` | Linux/Mac | Backend only |
| `start-frontend.ps1` | Windows | Frontend only |
| `start-frontend.sh` | Linux/Mac | Frontend only |
| `stop.bat` | Windows | Easy stop (runs stop.ps1) |
| `stop.ps1` | Windows | PowerShell stop script |
| `stop.sh` | Linux/Mac | Bash stop script |

## 🔧 Manual Commands

If you prefer to run commands manually:

### Backend
```bash
# Activate virtual environment
.\env\Scripts\Activate.ps1  # Windows PowerShell
.\env\Scripts\activate.bat  # Windows CMD
source env/bin/activate     # Linux/Mac

# Start backend
cd backend
python -m uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm run dev
```

## ⚙️ Configuration

Configuration is stored in:
- `backend/.env` - Backend environment variables
- `backend/config.py` - Backend settings
- `frontend/vite.config.ts` - Frontend build configuration

## 🆘 Help

If you encounter issues:
1. Check [INSTALL.md](INSTALL.md) for troubleshooting
2. Check [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for common fixes
3. View API documentation at http://localhost:8000/api/docs (when running)
4. Open an issue on GitHub

---

**Happy Manufacturing! 🏭**
