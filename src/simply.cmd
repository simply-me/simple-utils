@echo off
SETLOCAL EnableExtensions

:: 1. Auto-Bootstrap Check
if not exist "%~dp0py_lib\.venv" (
    echo [Launcher] Environment missing. Initializing production setup...
    if exist "%~dp0setup_env.cmd" (
        call "%~dp0setup_env.cmd"
    ) else (
        echo [ERROR] setup_env.cmd is missing from src folder! Cannot initialize.
        pause
        exit /b 1
    )
)

:: 2. Activate Environment
call "%~dp0py_lib\.venv\Scripts\activate.bat"

:: 3. Forward parameters to the core routing script
python "%~dp0py_lib\main.py" %*

if errorlevel 1 (
    echo.
    echo [CRITICAL] Application execution failed.
    echo.
    pause
    exit /b 1
)
exit /b 0
