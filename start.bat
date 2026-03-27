@echo off
echo ==============================
echo   RideSurge RL - Starting...
echo ==============================

:: Start Backend (FastAPI)
echo [1/2] Starting Backend on port 8000...
start "RideSurge Backend" cmd /k "cd /d %~dp0backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

:: Wait for backend to initialize
timeout /t 5 /nobreak > nul

:: Start Frontend (Vite + React)
echo [2/2] Starting Frontend on port 5173...
start "RideSurge Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo ==============================
echo   Both servers starting!
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:5173
echo ==============================
pause
