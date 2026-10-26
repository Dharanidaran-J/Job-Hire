# ========================================================
# ChallengeHire - Automated Push to Dharanidaran-J/Job-Hire
# ========================================================

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "   Pushing to https://github.com/Dharanidaran-J/Job-Hire.git" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# 1. Check Git & Add to PATH if needed
$gitExe = "git"
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    if (Test-Path "C:\Program Files\Git\cmd\git.exe") {
        $env:Path = "C:\Program Files\Git\cmd;" + $env:Path
    } elseif (Test-Path "C:\Program Files\Git\bin\git.exe") {
        $env:Path = "C:\Program Files\Git\bin;" + $env:Path
    } else {
        Write-Host "[X] Git is not installed or not in PATH." -ForegroundColor Red
        Write-Host "Please install Git from https://git-scm.com/download/win" -ForegroundColor Yellow
        exit
    }
}

$ver = git --version
Write-Host "[✓] Git detected: $ver" -ForegroundColor Green

# 2. Init
if (-not (Test-Path ".git")) {
    git init
    Write-Host "[1/5] Git repository initialized." -ForegroundColor Green
}

# 3. Ensure identity
$authorEmail = git config user.email 2>$null
if (-not $authorEmail) {
    git config user.name "Dharanidaran J"
    git config user.email "dharanidaran@users.noreply.github.com"
    Write-Host "[2/5] Configured Git user identity: Dharanidaran J" -ForegroundColor Green
} else {
    Write-Host "[2/5] Author identity verified: $authorEmail" -ForegroundColor Green
}

# 4. Unstage sensitive files
git rm --cached .env 2>$null
git rm --cached challengehire.db 2>$null

# 5. Stage all files
Write-Host "[3/5] Staging files..." -ForegroundColor Cyan
git add .

# 6. Commit
Write-Host "[4/5] Creating commit..." -ForegroundColor Cyan
git commit -m "Initial commit: Complete ChallengeHire Full-Stack Platform" 2>$null

# 7. Branch and Remote
Write-Host "[5/5] Linking remote and pushing to main branch..." -ForegroundColor Cyan
git branch -M main
git remote remove origin 2>$null
git remote add origin https://github.com/Dharanidaran-J/Job-Hire.git

Write-Host "Uploading to GitHub..." -ForegroundColor Yellow
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================================" -ForegroundColor Green
    Write-Host "   SUCCESS! Website pushed to GitHub successfully!" -ForegroundColor Green
    Write-Host "   View repository: https://github.com/Dharanidaran-J/Job-Hire" -ForegroundColor Green
    Write-Host "========================================================" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "Attempting push with pull/rebase if remote has existing README/files..." -ForegroundColor Yellow
    git pull origin main --allow-unrelated-histories --no-edit 2>$null
    git push -u origin main
}
