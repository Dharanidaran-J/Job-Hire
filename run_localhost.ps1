# ========================================================
# ChallengeHire - Localhost Launcher for PowerShell
# ========================================================

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "   Starting ChallengeHire on Localhost (127.0.0.1:5000)" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# 1. Verify Python
try {
    $pyVer = python --version
    Write-Host "[✓] Python is installed: $pyVer" -ForegroundColor Green
} catch {
    Write-Host "[X] Python is not installed or not in PATH." -ForegroundColor Red
    Write-Host "Please install Python from https://www.python.org/downloads/" -ForegroundColor Yellow
    exit
}

# 2. Virtual Environment
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "[1/3] Setting up virtual environment (venv)..." -ForegroundColor Yellow
    python -m venv venv
}

if (Test-Path "venv\Scripts\Activate.ps1") {
    & .\venv\Scripts\Activate.ps1
}

# 3. Dependencies
Write-Host "[2/3] Verifying dependencies (Flask, SQLAlchemy, psycopg2)..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet

# 4. Open Browser & Run
Write-Host "[3/3] Starting web server..." -ForegroundColor Green
Write-Host ""
Write-Host "========================================================" -ForegroundColor Green
Write-Host "   Web Server: http://127.0.0.1:5000" -ForegroundColor Green
Write-Host "   Press Ctrl+C to stop the server." -ForegroundColor Gray
Write-Host "========================================================" -ForegroundColor Green
Write-Host ""

# Open default browser
Start-Process "http://127.0.0.1:5000"

# Start Flask
python run.py
