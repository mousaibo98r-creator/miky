@echo off
echo ===================================================
echo   EXPORT ANALYTICS PLATFORM - GITHUB PUSH SCRIPT
echo ===================================================
echo.

echo 1. Checking for Git installation...
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Git is not installed or not in your PATH.
    echo Please install Git from https://git-scm.com/downloads
    pause
    exit /b
)

echo 2. Initializing Git repository...
if not exist .git (
    git init
) else (
    echo Git repository already initialized.
)

echo.
echo 3. Adding files to staging area...
git add .

echo.
echo 4. Committing changes...
git commit -m "Update Export Analytics Platform with JSON integration"
if %errorlevel% neq 0 (
    echo [INFO] No changes to commit (or commit failed). Proceeding...
)

echo.
REM Setting remote to the repository derived from your link
set repo_url=https://github.com/mousaibo98r-creator/miky.git

echo 5. Configuring remote repository...
echo Target Repository: %repo_url%

REM Remove existing origin if it exists to avoid conflict
git remote remove origin 2>nul
git remote add origin %repo_url%

echo.
echo 6. Pushing to GitHub...
echo.
git branch -M main
git push -u origin main --force

echo.
echo ===================================================
if %errorlevel% equ 0 (
    echo [SUCCESS] Code pushed successfully to GitHub!
    echo Opening repository in your browser...
    timeout /t 3 >nul
    start %repo_url%
) else (
    echo [ERROR] Failed to push code. Please check the error messages above.
)
echo ===================================================
echo.
pause
