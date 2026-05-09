@echo off
title DRO Setup - Agentic Commerce Engine
mode con: cols=80 lines=30
setlocal enabledelayedexpansion

echo ============================================================
echo   🚀 DRO - Agentic Commerce Engine Setup
echo   v2.0.0
echo ============================================================
echo.

:: Check Python
echo [1/4] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo   ⚠️  Python not found. Installing Python 3.12...
    echo   Downloading...
    curl -L -o "%TEMP%\python-installer.exe" https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe
    echo   Installing (this may take a minute)...
    "%TEMP%\python-installer.exe" /quiet InstallAllUsers=1 PrependPath=1
    echo   ✅ Python installed
) else (
    for /f "tokens=2" %%a in ('python --version 2^>^&1') do echo   ✅ Python %%a
)

:: Create virtual environment
echo [2/4] Setting up virtual environment...
if not exist "venv\" (
    python -m venv venv
    echo   ✅ Virtual environment created
) else (
    echo   ✅ Virtual environment exists
)

:: Install dependencies
echo [3/4] Installing dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt -q
echo   ✅ Dependencies installed

:: Setup .env
echo [4/4] Configuring environment...
if not exist ".env" (
    copy .env.example .env >nul
    echo   ✅ .env file created
    echo.
    echo   ⚠️  Please edit .env with your API keys:
    echo      notepad .env
) else (
    echo   ✅ .env file exists
)

:: Done
echo.
echo ============================================================
echo   ✅ Setup Complete!
echo ============================================================
echo.
echo   Quick start:
echo   -----------------------------------------
echo   Activate:  venv\Scripts\activate
echo   Run API:   python main.py server
echo   Dashboard: python main.py dashboard
echo   Doctor:    python main.py doctor
echo   -----------------------------------------
echo.
echo   📍 API:        http://localhost:8000
echo   📍 Dashboard:  http://localhost:8501
echo   📍 API Docs:   http://localhost:8000/docs
echo.
echo   Press any key to exit...
pause >nul
