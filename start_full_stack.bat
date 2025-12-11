@echo off
echo ========================================
echo Starting Food Advisor Full Stack
echo ========================================

echo.
echo [1/3] Installing backend dependencies...
pip install email-validator -q

echo.
echo [2/3] Starting Backend API...
start "Backend API" cmd /k "cd /d %~dp0 && python run_server.py"

timeout /t 5 /nobreak > nul

echo.
echo [3/3] Starting Frontend...
start "Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ========================================
echo Full Stack Started!
echo ========================================
echo.
echo Backend API: http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to exit...
pause > nul
