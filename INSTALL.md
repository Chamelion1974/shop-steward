# Shop Steward Hub - Installation Guide

Complete installation and setup guide for The Hub.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Installation](#quick-installation)
  - [Windows](#windows)
  - [Linux/Mac](#linuxmac)
- [Manual Installation](#manual-installation)
- [Starting the Hub](#starting-the-hub)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Production Deployment](#production-deployment)

---

## Prerequisites

Before installing Shop Steward Hub, ensure you have the following installed:

### Required Software

1. **Python 3.11 or higher**
   - Download from: https://www.python.org/downloads/
   - Verify: `python --version` or `python3 --version`

2. **Node.js 18 or higher**
   - Download from: https://nodejs.org/
   - Verify: `node --version`

3. **npm** (comes with Node.js)
   - Verify: `npm --version`

### Optional (for production)

- **PostgreSQL** (recommended for multi-user production environments)
- **Nginx** or **Apache** (for reverse proxy)
- **systemd** or **Windows Service** (for auto-start on boot)

---

## Quick Installation

### Windows

1. **Download or Clone** the repository:
   ```powershell
   git clone https://github.com/Chamelion1974/shop-steward.git
   cd shop-steward
   ```

2. **Run the installation script**:
   ```powershell
   .\install.ps1
   ```

3. **Wait for completion** - The script will:
   - Check prerequisites
   - Create Python virtual environment
   - Install backend dependencies
   - Install frontend dependencies
   - Create necessary directories
   - Copy configuration templates

4. **Start the Hub**:
   ```powershell
   .\start.ps1
   ```

That's it! The Hub will open in separate terminal windows for backend and frontend.

### Linux/Mac

1. **Download or Clone** the repository:
   ```bash
   git clone https://github.com/Chamelion1974/shop-steward.git
   cd shop-steward
   ```

2. **Make scripts executable**:
   ```bash
   chmod +x install.sh start.sh start-backend.sh start-frontend.sh
   ```

3. **Run the installation script**:
   ```bash
   ./install.sh
   ```

4. **Start the Hub**:
   ```bash
   ./start.sh
   ```

The Hub will start with both backend and frontend servers running.

---

## Manual Installation

If you prefer to install manually or need more control:

### Backend Setup

1. **Create a virtual environment**:
   ```bash
   # Windows
   python -m venv env
   .\env\Scripts\Activate.ps1
   
   # Linux/Mac
   python3 -m venv env
   source env/bin/activate
   ```

2. **Install backend dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   cd ..
   ```

### Frontend Setup

1. **Install frontend dependencies**:
   ```bash
   cd frontend
   npm install
   cd ..
   ```

### Configuration

1. **Create .env file**:
   ```bash
   # Windows
   copy backend\.env.example backend\.env
   
   # Linux/Mac
   cp backend/.env.example backend/.env
   ```

2. **Edit backend/.env** to customize settings (optional)

3. **Create necessary directories**:
   ```bash
   mkdir -p backend/uploads backend/modules uploads modules
   ```

---

## Starting the Hub

### Option 1: All-in-One Start (Recommended)

**Windows:**
```powershell
.\start.ps1
```

**Linux/Mac:**
```bash
./start.sh
```

This starts both backend and frontend servers.

### Option 2: Start Servers Separately

**Backend:**
```powershell
# Windows
.\start-backend.ps1

# Linux/Mac
./start-backend.sh
```

**Frontend:**
```powershell
# Windows
.\start-frontend.ps1

# Linux/Mac
./start-frontend.sh
```

### Access the Application

Once both servers are running:

- **Frontend (Main Application)**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs

### Default Login Credentials

```
Username: admin
Password: admin123
```

⚠️ **IMPORTANT**: Change the password immediately after first login!

---

## Configuration

### Environment Variables

Edit `backend/.env` to customize:

#### Security (Required for Production)

```bash
# Generate a secure secret key:
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Then set it in .env:
SECRET_KEY="your-generated-secret-key-here"
```

#### Database

**SQLite (Default - Single Machine):**
```bash
DATABASE_URL="sqlite:///./shop_steward.db"
```

**PostgreSQL (Recommended for Production):**
```bash
DATABASE_URL="postgresql://username:password@localhost/shop_steward"
```

#### File Uploads

```bash
UPLOAD_DIR="./uploads"
MAX_UPLOAD_SIZE=104857600  # 100MB
```

#### CORS (if frontend is on different domain)

```bash
CORS_ORIGINS=["http://your-domain.com:3000","http://your-domain.com:5173"]
```

### Port Configuration

**Backend Port** (default: 8000):
Edit in `start-backend.ps1` or `start-backend.sh`:
```bash
# Change --port 8000 to your preferred port
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

**Frontend Port** (default: 5173):
Edit `frontend/vite.config.ts`:
```typescript
export default defineConfig({
  server: {
    port: 3000  // Change to your preferred port
  }
})
```

---

## Troubleshooting

### Common Issues

#### "Virtual environment not found"

**Solution**: Run the installation script first:
```bash
# Windows
.\install.ps1

# Linux/Mac
./install.sh
```

#### "Python not found" or "Node.js not found"

**Solution**: Install the prerequisites listed above.

#### "Port already in use"

**Solution**: 
1. Check what's using the port:
   ```bash
   # Windows
   netstat -ano | findstr :8000
   
   # Linux/Mac
   lsof -i :8000
   ```

2. Kill the process or change the port in configuration

#### Backend fails to start

**Check:**
1. Virtual environment is activated
2. All dependencies installed: `pip install -r backend/requirements.txt`
3. Database file is accessible (or database server is running for PostgreSQL)

#### Frontend fails to start

**Check:**
1. Node modules installed: `npm install` in frontend directory
2. Backend is running (frontend needs backend API)

#### Can't login after installation

**Solution**: The admin user is created on first startup. If you had an old database:
1. Delete `backend/shop_steward.db`
2. Restart backend - it will create a fresh database with admin user

Or run the update script:
```bash
# Windows
.\env\Scripts\python.exe .\backend\update_admin_email.py

# Linux/Mac
./env/bin/python ./backend/update_admin_email.py
```

### Getting Help

1. Check the logs in backend terminal for error messages
2. Check `backend/shop_steward.log` for detailed logs
3. Visit API docs at http://localhost:8000/api/docs to test API endpoints
4. Open an issue on GitHub with error details

---

## Production Deployment

### Security Checklist

- [ ] Change default admin password
- [ ] Generate and set a secure `SECRET_KEY` in .env
- [ ] Use PostgreSQL instead of SQLite
- [ ] Set `DEBUG=False` in .env
- [ ] Configure firewall to restrict port access
- [ ] Use HTTPS with SSL certificates
- [ ] Set up regular database backups
- [ ] Configure proper CORS origins for your domain

### Recommended Setup

1. **Database**: PostgreSQL
   ```bash
   # Install PostgreSQL
   # Create database
   createdb shop_steward
   
   # Update .env
   DATABASE_URL="postgresql://user:password@localhost/shop_steward"
   ```

2. **Web Server**: Nginx or Apache as reverse proxy
   - Proxy http://localhost:8000 (backend)
   - Serve built frontend files (run `npm run build` in frontend)

3. **Process Manager**: 
   - **Linux**: systemd service
   - **Windows**: Windows Service or Task Scheduler

4. **SSL Certificate**: Use Let's Encrypt or your certificate provider

### Building for Production

**Frontend:**
```bash
cd frontend
npm run build
```

This creates optimized static files in `frontend/dist/` that can be served by Nginx/Apache.

**Backend:**
```bash
# Use a production WSGI server like gunicorn
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## Next Steps

After installation:

1. **Login** with default credentials
2. **Change admin password** in Settings → Password
3. **Create Hub Cap users** for your programmers/operators
4. **Explore modules** in the Modules page
5. **Create your first job** in the Jobs page

For detailed usage instructions, see the main [README.md](README.md).

---

## Support

For issues, questions, or suggestions:
- GitHub Issues: https://github.com/Chamelion1974/shop-steward/issues
- Documentation: See README.md and WORKFLOW.md

---

**Happy Manufacturing! 🏭**
