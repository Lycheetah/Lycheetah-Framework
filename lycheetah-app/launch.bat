@echo off
echo.
echo   Lycheetah Library Launcher
echo   --------------------------
echo.

:: Check if dist/ exists
if not exist "dist\" (
  echo   [!] No dist/ directory found.
  echo   Run "npm run build" first, then double-click launch.bat again.
  echo.
  pause
  exit /b 1
)

:: Launch the local server
node launch.js
