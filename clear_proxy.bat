@echo off
echo [Antigravity] Clearing Proxy Settings...
echo Resetting to Direct Connection...

:: Disable Proxy
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable /t REG_DWORD /d 0 /f

echo [SUCCESS] Proxy Cleared. You are now on Direct Connection.
pause
