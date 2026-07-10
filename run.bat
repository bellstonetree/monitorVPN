@echo off
setlocal

cd /d "%~dp0"

set "PYTHON_EXE="
set "PYTHON_ARGS="

where py >nul 2>nul
if not errorlevel 1 (
    py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)" >nul 2>nul
    if not errorlevel 1 (
        set "PYTHON_EXE=py"
        set "PYTHON_ARGS=-3"
    )
)

if not defined PYTHON_EXE (
    where python >nul 2>nul
    if not errorlevel 1 (
        python -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)" >nul 2>nul
        if not errorlevel 1 set "PYTHON_EXE=python"
    )
)

if not defined PYTHON_EXE if exist "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" (
    set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python314\python.exe"
)

if not defined PYTHON_EXE if exist "C:\Python314\python.exe" (
    set "PYTHON_EXE=C:\Python314\python.exe"
)

if not defined PYTHON_EXE (
    echo VPN Monitor cannot start because a required component is missing:
    echo.
    echo - Python 3.9+
    echo.
    echo Install Python from https://www.python.org/downloads/windows/ and try again.
    pause
    exit /b 1
)

"%PYTHON_EXE%" %PYTHON_ARGS% vpn_monitor.py
set "EXIT_CODE=%errorlevel%"
if not "%EXIT_CODE%"=="0" pause
exit /b %EXIT_CODE%
