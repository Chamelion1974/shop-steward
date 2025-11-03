@echo off
REM Shop Steward Hub - Windows Batch Stop Script
REM This runs the PowerShell stop script

echo ================================================
echo    Stopping Shop Steward Hub
echo ================================================
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0stop.ps1"

pause
