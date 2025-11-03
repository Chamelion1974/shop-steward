# Shop Steward Hub - Quick Reference

Quick commands and reference for daily use.

## Installation & Setup

### First Time Setup

**Windows:**
```powershell
.\install.ps1
```

**Linux/Mac:**
```bash
chmod +x install.sh start.sh stop.sh
./install.sh
```

---

## Starting & Stopping

### Start Everything

**Windows:**
```powershell
.\start.ps1
```

**Linux/Mac:**
```bash
./start.sh
```

### Start Individual Services

**Backend Only:**
```powershell
# Windows
.\start-backend.ps1

# Linux/Mac
./start-backend.sh
```

**Frontend Only:**
```powershell
# Windows
.\start-frontend.ps1

# Linux/Mac
./start-frontend.sh
```

### Stop Everything

**Windows:**
```powershell
.\stop.ps1
```

**Linux/Mac:**
```bash
./stop.sh
```

Or press `Ctrl+C` in the terminal windows.

---

## Access Points

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:5173 | Main application interface |
| **Backend API** | http://localhost:8000 | REST API endpoints |
| **API Docs** | http://localhost:8000/api/docs | Interactive API documentation |

---

## Default Credentials

```
Username: admin
Password: admin123
```

⚠️ **Change immediately after first login!**

To change: Login → Settings → Password tab

---

## Common Tasks

### Update Dependencies

**Backend:**
```bash
# Activate environment first
.\env\Scripts\Activate.ps1  # Windows
source env/bin/activate      # Linux/Mac

# Update
cd backend
pip install -r requirements.txt --upgrade
```

**Frontend:**
```bash
cd frontend
npm update
```

### Reset Admin Password

If you forget the admin password:

```bash
# Windows
.\env\Scripts\python.exe .\backend\update_admin_email.py

# Linux/Mac
./env/bin/python ./backend/update_admin_email.py
```

Then check the script or manually reset in database.

### Backup Database

**SQLite (default):**
```bash
# Copy the database file
copy backend\shop_steward.db backend\shop_steward.db.backup  # Windows
cp backend/shop_steward.db backend/shop_steward.db.backup    # Linux/Mac
```

**PostgreSQL:**
```bash
pg_dump shop_steward > backup.sql
```

### View Logs

**Backend logs:**
- Console: Check the backend terminal window
- File: `backend/shop_steward.log`

**Frontend logs:**
- Console: Check the frontend terminal window
- Browser: Press F12 → Console tab

---

## Project Structure

```
shop-steward/
├── backend/              # FastAPI backend
│   ├── app/             # Application code
│   │   ├── api/         # API endpoints
│   │   ├── core/        # Security, auth
│   │   ├── models/      # Database models
│   │   ├── schemas/     # Pydantic schemas
│   │   └── modules/     # Extension modules
│   ├── uploads/         # Uploaded files
│   ├── shop_steward.db  # SQLite database
│   └── requirements.txt # Python dependencies
│
├── frontend/            # React frontend
│   ├── src/
│   │   ├── components/  # Reusable components
│   │   ├── pages/       # Page components
│   │   ├── services/    # API client
│   │   └── stores/      # State management
│   └── package.json     # Node dependencies
│
├── modules/             # Custom modules
├── uploads/             # Additional uploads
├── env/                 # Python virtual environment
│
├── install.ps1          # Windows installer
├── install.sh           # Linux/Mac installer
├── start.ps1            # Windows startup
├── start.sh             # Linux/Mac startup
├── stop.ps1             # Windows stop script
└── stop.sh              # Linux/Mac stop script
```

---

## Troubleshooting Quick Fixes

### Backend won't start

1. Check Python virtual environment is activated
2. Reinstall dependencies: `pip install -r backend/requirements.txt`
3. Check port 8000 is available: `netstat -ano | findstr :8000`

### Frontend won't start

1. Reinstall dependencies: `npm install` in frontend folder
2. Clear cache: `npm cache clean --force`
3. Check port 5173 is available

### Can't login

1. Check backend is running
2. Reset database: Delete `backend/shop_steward.db` and restart
3. Check browser console (F12) for errors

### Database errors

1. Make sure only one backend instance is running
2. Check file permissions on `shop_steward.db`
3. Delete and recreate: Restart backend to create fresh DB

---

## Production Checklist

Before deploying to production:

- [ ] Run `npm run build` in frontend directory
- [ ] Set `DEBUG=False` in backend/.env
- [ ] Change `SECRET_KEY` to a secure random value
- [ ] Use PostgreSQL instead of SQLite
- [ ] Change admin password
- [ ] Set up SSL/HTTPS
- [ ] Configure firewall rules
- [ ] Set up automated backups
- [ ] Configure CORS for your domain
- [ ] Use a process manager (systemd, supervisor, etc.)

---

## Getting Help

1. **Documentation**: See [INSTALL.md](INSTALL.md) for detailed installation
2. **Main README**: See [README.md](README.md) for feature documentation
3. **API Docs**: http://localhost:8000/api/docs when backend is running
4. **Issues**: Report bugs or request features on GitHub

---

## Quick Commands Cheat Sheet

```powershell
# Windows PowerShell
.\install.ps1           # Install everything
.\start.ps1             # Start both servers
.\stop.ps1              # Stop both servers
.\start-backend.ps1     # Start backend only
.\start-frontend.ps1    # Start frontend only
```

```bash
# Linux/Mac Bash
./install.sh            # Install everything
./start.sh              # Start both servers
./stop.sh               # Stop both servers
./start-backend.sh      # Start backend only
./start-frontend.sh     # Start frontend only
```

---

**Happy Manufacturing! 🏭**
