@echo off
setlocal

cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
    py -3w vpn_monitor.py
    exit /b %errorlevel%
)

where pythonw >nul 2>nul
if %errorlevel%==0 (
    pythonw vpn_monitor.py
    exit /b %errorlevel%
)

where python >nul 2>nul
if %errorlevel%==0 (
    python vpn_monitor.py
    exit /b %errorlevel%
)

if exist "%LOCALAPPDATA%\Programs\Python\Python314\pythonw.exe" (
    "%LOCALAPPDATA%\Programs\Python\Python314\pythonw.exe" vpn_monitor.py
    exit /b %errorlevel%
)

if exist "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" (
    "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" vpn_monitor.py
    exit /b %errorlevel%
)

echo Python 3 was not found.
echo Install Python 3 from https://www.python.org/downloads/windows/ and try again.
pause
exit /b 1
