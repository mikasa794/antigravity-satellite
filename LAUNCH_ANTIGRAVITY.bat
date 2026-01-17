@echo off
title Antigravity Lens Launcher 🚀
color 0A
cd /d "%~dp0"

echo.
echo  =======================================================
echo   ANTIGRAVITY LENS - SYSTEM LINK
echo  =======================================================
echo.

echo  [1/3] Configuring Neural Pathways (Ollama CORS)...
setx OLLAMA_ORIGINS "*" >nul

echo  [2/3] Checking AI Status...
tasklist /FI "IMAGENAME eq ollama.exe" 2>NUL | find /I /N "ollama.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo        - Ollama is ALREADY RUNNING.
) else (
    echo        - Starting Ollama...
    start /b ollama serve >nul 2>&1
)

echo  [3/3] Launching The Garden...
echo.
echo  Please wait. Chrome will open automatically.
echo  (Press 'R' in this window to Reload after changes)
echo.

cd antigravity_lens
flutter run -d chrome --web-renderer html

pause
