# Shop Steward Hub - Frontend Startup Script (Windows)

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   Shop Steward Hub - Frontend Server" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Change to frontend directory
Set-Location frontend

Write-Host "Starting Vite development server..." -ForegroundColor Yellow
Write-Host ""

# Start Vite dev server
npm run dev

# Keep window open if there's an error
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "✗ Frontend server stopped with errors" -ForegroundColor Red
    Read-Host "Press Enter to close"
}
