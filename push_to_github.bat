@echo off
title Push ChallengeHire to GitHub
color 0b

echo ========================================================
echo   Pushing ChallengeHire to:
echo   https://github.com/Dharanidaran-J/Job-Hire.git
echo ========================================================
echo.

cd /d "%~dp0"

:: 1. Add Git to PATH if not already found
where git >nul 2>nul
if %errorlevel% neq 0 (
    if exist "C:\Program Files\Git\cmd\git.exe" (
        set "PATH=C:\Program Files\Git\cmd;%PATH%"
    ) else if exist "C:\Program Files\Git\bin\git.exe" (
        set "PATH=C:\Program Files\Git\bin;%PATH%"
    ) else (
        echo [ERROR] Git is not installed on your system!
        echo.
        echo Please install Git from: https://git-scm.com/download/win
        echo or install GitHub Desktop: https://desktop.github.com
        echo.
        pause
        exit /b
    )
)

:: 2. Initialize Git if needed
echo [1/5] Checking Git repository...
if not exist ".git" (
    git init
)

:: 3. Ensure Git identity is configured
echo [2/5] Checking author identity...
git config user.email >nul 2>nul
if %errorlevel% neq 0 (
    git config user.name "Dharanidaran J"
    git config user.email "dharanidaran@users.noreply.github.com"
    echo [OK] Set author identity as Dharanidaran J.
)

:: 4. Safety: Ensure sensitive files are not tracked
git rm --cached .env >nul 2>nul
git rm --cached challengehire.db >nul 2>nul

:: 5. Stage files
echo [3/5] Staging files...
git add .

:: 6. Commit
echo [4/5] Creating commit...
git commit -m "Initial commit: Complete ChallengeHire Full-Stack Platform" >nul 2>nul
if %errorlevel% neq 0 (
    git commit -m "Update ChallengeHire project files" >nul 2>nul
)

:: 7. Set main branch & remote
echo [5/5] Linking remote repository and pushing...
git branch -M main
git remote remove origin >nul 2>nul
git remote add origin https://github.com/Dharanidaran-J/Job-Hire.git

echo.
echo Uploading files to GitHub (main branch)...
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ========================================================
    echo   SUCCESS! Website is now live on GitHub!
    echo   Repository: https://github.com/Dharanidaran-J/Job-Hire
    echo ========================================================
) else (
    echo.
    echo [NOTE] If git rejected because remote has existing commits, trying to merge...
    git pull origin main --allow-unrelated-histories --no-edit >nul 2>nul
    git push -u origin main
)

echo.
pause
