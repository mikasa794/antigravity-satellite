@echo off
echo [Antigravity] Fixing Proxy Connection...
echo Setting Proxy to 127.0.0.1:7897...

:: Add Proxy Address
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyServer /t REG_SZ /d "127.0.0.1:7897" /f

:: Enable Proxy
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable /t REG_DWORD /d 1 /f

:: Set Bypass List (Localhost, etc.)
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyOverride /t REG_SZ /d "localhost;127.0.0.1;<local>;10.0.0.0/8;172.16.0.0/12;192.168.0.0/16" /f

echo [SUCCESS] Proxy Set. You should be able to connect to Antigravity now.
pause
