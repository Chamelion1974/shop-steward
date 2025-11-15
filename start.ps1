# Shop Steward Hub - Unified Startup Script (Windows)
# This script starts both backend and frontend servers

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   Starting Shop Steward Hub" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "env\Scripts\Activate.ps1")) {
    Write-Host "✗ Virtual environment not found!" -ForegroundColor Red
    Write-Host "  Please run install.ps1 first" -ForegroundColor Red
    exit 1
}

# Check if node_modules exists
if (-not (Test-Path "frontend\node_modules")) {
    Write-Host "✗ Frontend dependencies not found!" -ForegroundColor Red
    Write-Host "  Please run install.ps1 first" -ForegroundColor Red
    exit 1
}

Write-Host "Starting backend server..." -ForegroundColor Yellow
$backendProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", "& '.\start-backend.ps1'" -PassThru

Start-Sleep -Seconds 2

Write-Host "Starting frontend server..." -ForegroundColor Yellow
$frontendProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", "& '.\start-frontend.ps1'" -PassThru

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   Shop Steward Hub is starting!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend and frontend are starting in separate windows..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Once both servers are ready, access the Hub at:" -ForegroundColor Yellow
Write-Host "  Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host "  Backend:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "  API Docs: http://localhost:8000/api/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Default credentials:" -ForegroundColor Yellow
Write-Host "  Username: admin" -ForegroundColor Cyan
Write-Host "  Password: admin123" -ForegroundColor Cyan
Write-Host ""
Write-Host "To stop the servers, close the backend and frontend terminal windows" -ForegroundColor Yellow
Write-Host "or press Ctrl+C in each window." -ForegroundColor Yellow
Write-Host ""
