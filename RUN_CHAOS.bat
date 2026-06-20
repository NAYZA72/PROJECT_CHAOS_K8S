@echo off
title C.H.A.O.S. - Command Handling AI Operating System
echo.
echo   ========================================
echo     C.H.A.O.S. is starting up...
echo   ========================================
echo.
set PYTHONIOENCODING=utf-8

REM Start a background task to open the browser after delay
start /min cmd /c "timeout /t 5 /nobreak >nul & start http://localhost:8000"

REM Run CHAOS in foreground (keeps console open)
"%LOCALAPPDATA%\Microsoft\WindowsApps\python3.11.exe" "%~dp0CHAOS.py"
pause
