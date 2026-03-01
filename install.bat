@echo off
title DailyBill Setup
cd /d %~dp0

echo ========================================
echo   DailyBill - Auto Installer
echo ========================================
echo.

echo [1/2] Creating virtual environment...
if not exist venv (
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Please install Python 3.10+ first
        echo Download from: https://www.python.org/downloads/
        pause
        exit /b 1
    )
)
echo OK

echo.
echo [2/2] Installing dependencies...

REM Try different Python paths
if exist venv\Scripts\pip.exe (
    venv\Scripts\pip.exe install openpyxl PyYAML
) else if exist venv\Scripts\python.exe (
    venv\Scripts\python.exe -m pip install openpyxl PyYAML
) else if exist venv\bin\pip (
    venv\bin\pip install openpyxl PyYAML
) else if exist venv\bin\python.exe (
    venv\bin\python.exe -m pip install openpyxl PyYAML
) else (
    echo ERROR: Cannot find pip in virtual environment
    pause
    exit /b 1
)

if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Setup Complete!
echo   Double-click start.bat to run
echo ========================================
pause
