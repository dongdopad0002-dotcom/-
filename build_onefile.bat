@echo off
setlocal
cd /d "%~dp0"

echo ==========================================
echo JeongSoyoonAI - single EXE build
echo ==========================================

python -m pip install -r requirements.txt
if errorlevel 1 exit /b 1

python -m playwright install chromium
if errorlevel 1 exit /b 1

python -m pip install pyinstaller
if errorlevel 1 exit /b 1

python -m PyInstaller --clean --noconfirm windows_onefile.spec
if errorlevel 1 exit /b 1

echo.
echo Build complete:
echo   dist\JeongSoyoonAI.exe
echo.
echo This is the single-file executable. No COLLECT folder is produced.
pause
