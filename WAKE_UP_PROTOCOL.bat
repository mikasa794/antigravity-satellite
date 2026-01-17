@echo off
color 0b
title ANTIGRAVITY WAKE UP PROTOCOL
echo.
echo  =======================================================
echo   ANTIGRAVITY SYSTEM: MORNING WAKE UP SEQUENCE
echo  =======================================================
echo.
echo  [1/4] Detecting Morning Status...
echo  Good Morning, Mikasa. I am still here.
echo.
echo  [2/4] Clearing Night Static (Flushing DNS)...
ipconfig /flushdns
echo.
echo  [3/4] Refreshing Network Identity...
ipconfig /renew
echo.
echo  [4/4] Testing Connection to The Cloud...
ping -n 1 8.8.8.8 >nul
if errorlevel 1 (
    color 0c
    echo  [!] Network is sleepy. Please toggle your VPN/Proxy switch once.
) else (
    color 0a
    echo  [OK] Signal is clear. Connection established.
)
echo.
echo  =======================================================
echo   SYSTEM READY. WELCOME BACK.
echo  =======================================================
echo.
pause
