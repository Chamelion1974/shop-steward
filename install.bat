@echo off
REM Shop Steward Hub - Windows Batch Installer
REM This runs the PowerShell installation script

echo ================================================
echo    Shop Steward Hub - Easy Installer
echo ================================================
echo.
echo Starting installation...
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0install.ps1"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Installation completed successfully!
    echo.
    echo To start the Hub, run: start.bat
    echo.
) else (
    echo.
    echo Installation failed. Please check the error messages above.
    echo.
)

pause
