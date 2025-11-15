# Shop Steward Hub - Quick Stop Script (Windows)

Write-Host "Stopping Shop Steward Hub servers..." -ForegroundColor Yellow

# Find and kill uvicorn (backend) processes
$uvicornProcesses = Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object {
    $_.MainWindowTitle -like "*uvicorn*" -or $_.CommandLine -like "*uvicorn*"
}

if ($uvicornProcesses) {
    $uvicornProcesses | Stop-Process -Force
    Write-Host "✓ Backend server stopped" -ForegroundColor Green
} else {
    Write-Host "! No backend server found running" -ForegroundColor Yellow
}

# Find and kill node (frontend) processes
$nodeProcesses = Get-Process -Name node -ErrorAction SilentlyContinue | Where-Object {
    $_.MainWindowTitle -like "*vite*" -or $_.CommandLine -like "*vite*"
}

if ($nodeProcesses) {
    $nodeProcesses | Stop-Process -Force
    Write-Host "✓ Frontend server stopped" -ForegroundColor Green
} else {
    Write-Host "! No frontend server found running" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Shop Steward Hub has been stopped" -ForegroundColor Cyan
