@echo off
setlocal
chcp 65001 >nul
title LAN-LMS - Full system test data - port 8081
cd /d "%~dp0"
set PYTHONUTF8=1
set PYTHONNOUSERSITE=1
set PYTHONDONTWRITEBYTECODE=1
set "LMS_TEST_PYTHON="
for %%P in (".venv-windows\Scripts\python.exe" ".venv\Scripts\python.exe") do (
    if not defined LMS_TEST_PYTHON if exist "%%~P" (
        "%%~P" -c "import jinja2" >nul 2>&1
        if not errorlevel 1 set "LMS_TEST_PYTHON=%%~P"
    )
)
if not defined LMS_TEST_PYTHON (
    python -c "import jinja2" >nul 2>&1
    if not errorlevel 1 set "LMS_TEST_PYTHON=python"
)
if not defined LMS_TEST_PYTHON (
    echo [ERROR] Run setup_windows.bat first.
    pause
    exit /b 1
)
echo Test URL: http://127.0.0.1:8081
echo Admin: testadmin / 111111
echo Student: DEMO001 / 111111
echo Data directory: sample-data\full-system
echo Open the URL above after the server prints Local URL.
echo Keep this window open. Press Ctrl+C to stop.
"%LMS_TEST_PYTHON%" -u -m scripts.seed_system_test --serve
if errorlevel 1 (
    echo [ERROR] See the message above. If port 8081 is busy, use --port with another port.
    pause
    exit /b 1
)
