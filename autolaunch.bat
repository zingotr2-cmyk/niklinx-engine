@echo off
title niklinx v2.0 — Auto Launch
color 0B
cls

echo.
echo ============================================================
echo             niklinx v2.0 — Auto Launch Sequence
echo ============================================================
echo.

:: ── Step 1: Git Add, Commit, Push ──
echo [1/4] Pushing code to GitHub ...
echo.
git add -A
if %errorlevel% neq 0 (
    echo [!!] git add failed — is this a git repo?
    pause
    exit /b 1
)

git commit -m "Auto-launch: niklinx v2.0"
git push -u origin main
if %errorlevel% neq 0 (
    echo [!!] git push failed — check remote origin and internet
    pause
    exit /b 1
)
echo.
echo [OK] Code pushed — GitHub Action deploying ...
echo.

:: ── Step 2: Generate Master License ──
echo [2/4] Generating Master License Key ...
echo.
python main.py license-gen < nul
echo.
echo [OK] Copy the key above ^& set it as DRO_LICENSE_KEY on Render
echo.

:: ── Step 3: Wait for deploy, then diagnose ──
echo [3/4] Waiting 90 seconds for Render to deploy ...
echo.
echo      https://dro-api.onrender.com
echo      https://dro-dashboard.onrender.com
echo.
ping -n 91 127.0.0.1 > nul

:: ── Step 4: Run Diagnostic ──
echo [4/4] Running production health check ...
echo.
python diagnose.py

echo.
echo ============================================================
echo        Launch complete — niklinx is OPEN for business
echo ============================================================
echo.
echo      API:         https://dro-api.onrender.com
echo      Dashboard:   https://dro-dashboard.onrender.com
echo      Docs:        https://dro-api.onrender.com/docs
echo.
pause
