@echo off
setlocal

cd /d "%~dp0"

where python >nul 2>nul
if %errorlevel%==0 (
    python vpn_monitor.py
    if %errorlevel%==0 exit /b 0
)

where py >nul 2>nul
if %errorlevel%==0 (
    py -3 vpn_monitor.py
    if %errorlevel%==0 exit /b 0
)

if exist "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" (
    "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" vpn_monitor.py
    if %errorlevel%==0 exit /b 0
)

if exist "C:\Python314\python.exe" (
    "C:\Python314\python.exe" vpn_monitor.py
    if %errorlevel%==0 exit /b 0
)

echo Python 3 was not found.
echo Install Python 3 from https://www.python.org/downloads/windows/ and try again.
pause
exit /b 1
