@echo off
title ChallengeHire - Localhost Server
color 0a

echo ========================================================
echo   Starting ChallengeHire on Localhost (127.0.0.1:5000)
echo ========================================================
echo.

cd /d "%~dp0"

:: 1. Check Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your PATH!
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    pause
    exit /b
)

:: 2. Check Virtual Environment
if not exist "venv\Scripts\activate.bat" (
    echo [1/3] Creating virtual environment (venv)...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [WARNING] Could not create venv. Running with global Python.
    )
)

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

:: 3. Install/Verify Dependencies
echo [2/3] Checking dependencies from requirements.txt...
pip install -r requirements.txt --quiet --no-warn-script-location

:: 4. Launch Browser after 2 seconds in background
echo [3/3] Launching web server and opening browser...
start "" timeout /t 2 /nobreak >nul & start http://127.0.0.1:5000

echo.
echo ========================================================
echo   ChallengeHire is LIVE on: http://127.0.0.1:5000
echo   Press CTRL+C in this window to stop the server.
echo ========================================================
echo.

python run.py
pause
