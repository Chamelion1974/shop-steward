# Shop Steward Hub - Backend Startup Script (Windows)

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   Shop Steward Hub - Backend Server" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\env\Scripts\Activate.ps1"

# Change to backend directory
Set-Location backend

Write-Host "Starting FastAPI server..." -ForegroundColor Yellow
Write-Host ""

# Start uvicorn server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Keep window open if there's an error
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "✗ Backend server stopped with errors" -ForegroundColor Red
    Read-Host "Press Enter to close"
}
