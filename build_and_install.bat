@echo off
echo ==========================================
echo       C.H.A.O.S. Installer Setup
echo ==========================================
echo.

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH! Please install Python 3.11+ to continue.
    pause
    exit /b 1
)

echo Installing dependencies...
pip install -r requirements.txt
pip install pyinstaller

echo.
echo Building CHAOS_Launcher.exe...
pyinstaller --onefile --noconsole --icon=chaos_new.ico --add-data "chaos_new.ico;." --add-data "chaos_icon_new.jpg;." --add-data "chaos.jpg;." --name CHAOS_Launcher launcher.py

echo.
echo ==========================================
echo Build Complete!
echo You can find the executable in the 'dist' folder.
echo You can right-click CHAOS_Launcher.exe and click "Send to" -^> "Desktop (create shortcut)"
echo ==========================================
pause
