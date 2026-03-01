@echo off
title DailyBill
cd /d %~dp0

REM Try different Python paths
if exist venv\Scripts\python.exe (
    venv\Scripts\python.exe src\main.py
) else if exist venv\bin\python.exe (
    venv\bin\python.exe src\main.py
) else (
    echo Please run install.bat first!
    pause
)
