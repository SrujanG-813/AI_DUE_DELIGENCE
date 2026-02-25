@echo off
echo ======================================================================
echo AI Due Diligence Engine - Frontend Server
echo ======================================================================
echo.
echo Installing dependencies (if needed)...
call npm install
echo.
echo Starting React development server on http://localhost:3000
echo.
echo Press CTRL+C to stop the server
echo ======================================================================
echo.

call npm run dev
