@echo off
REM Shop Steward Hub - Windows Batch Startup Script
REM This runs the PowerShell startup script

echo ================================================
echo    Starting Shop Steward Hub
echo ================================================
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0start.ps1"

pause
