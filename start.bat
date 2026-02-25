@echo off
echo ======================================================================
echo AI Due Diligence Engine - Starting All Services
echo ======================================================================
echo.
echo Starting Backend API Server (Port 8000)...
echo Starting Frontend Dev Server (Port 3000)...
echo.
echo Please wait while services start up...
echo ======================================================================
echo.

REM Start backend in a new window
start "Backend API - Port 8000" cmd /k "python api_server.py"

REM Wait 3 seconds for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend in a new window
start "Frontend UI - Port 3000" cmd /k "cd frontend && npm run dev"

REM Wait 5 seconds for frontend to start
timeout /t 5 /nobreak >nul

echo.
echo ======================================================================
echo Services Started Successfully!
echo ======================================================================
echo.
echo Backend API:  http://localhost:8000
echo Frontend UI:  http://localhost:3000
echo API Docs:     http://localhost:8000/docs
echo.
echo Opening browser in 3 seconds...
echo ======================================================================
echo.

REM Wait 3 seconds then open browser
timeout /t 3 /nobreak >nul
start http://localhost:3000

echo.
echo Browser opened! If not, manually navigate to: http://localhost:3000
echo.
echo To stop all services: Close the Backend and Frontend windows
echo.
pause
