@echo off
setlocal
chcp 65001 >nul
title LMS_LAN - Web LAN
cd /d "%~dp0"
set PYTHONUTF8=1
set PYTHONNOUSERSITE=1
set PYTHONDONTWRITEBYTECODE=1
set "LMS_PYTHON="
for %%P in (".venv-windows\Scripts\python.exe" ".venv\Scripts\python.exe") do (
    if not defined LMS_PYTHON if exist "%%~P" (
        "%%~P" -c "import jinja2" >nul 2>&1
        if not errorlevel 1 set "LMS_PYTHON=%%~P"
    )
)
if not defined LMS_PYTHON (
    call :try_base_python ".venv-windows"
)
if not defined LMS_PYTHON (
    call :try_base_python ".venv"
)
if not defined LMS_PYTHON (
    echo [ERROR] Run setup_windows.bat once, then open this file again.
    pause
    exit /b 1
)
"%LMS_PYTHON%" -u -m app.lan_launcher %*
set "LMS_EXIT_CODE=%ERRORLEVEL%"
if not "%LMS_EXIT_CODE%"=="0" echo [ERROR] Read the message above before closing this window.
if "%~1"=="--check" exit /b %LMS_EXIT_CODE%
pause
exit /b %LMS_EXIT_CODE%

:try_base_python
set "LMS_VENV=%~1"
if not exist "%LMS_VENV%\pyvenv.cfg" exit /b
set "LMS_HOME="
for /f "tokens=1,* delims==" %%A in ('findstr /b /c:"home =" "%LMS_VENV%\pyvenv.cfg"') do set "LMS_HOME=%%B"
if not defined LMS_HOME exit /b
set "LMS_HOME=%LMS_HOME:~1%"
set "LMS_BASE=%LMS_HOME%\python.exe"
if not exist "%LMS_BASE%" exit /b
set "LMS_SAVED_PYTHONPATH=%PYTHONPATH%"
set "PYTHONPATH=%CD%\%LMS_VENV%\Lib\site-packages"
"%LMS_BASE%" -c "import jinja2" >nul 2>&1
if errorlevel 1 (
    set "PYTHONPATH=%LMS_SAVED_PYTHONPATH%"
    exit /b
)
echo [INFO] Windows blocked the virtual environment executable; using its approved base Python.
set "LMS_PYTHON=%LMS_BASE%"
exit /b
