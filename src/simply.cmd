@echo off
SETLOCAL EnableExtensions

:: 0. Argument Check
if "%~1"=="" (
    echo [ERROR] No arguments provided. This script requires at least one argument.
    echo Usage: %~nx0 [arguments...]
    pause
    exit /b 1
)

:: Secure the working directory relative to this script
pushd "%~dp0"

:: 1. Auto-Bootstrap Check
if not exist "py_lib\.venv" (
    echo [Launcher] Environment missing. Initializing production setup...
    if exist "setup_env.cmd" (
        call "setup_env.cmd"
    ) else (
        echo [ERROR] setup_env.cmd is missing from src folder! Cannot initialize.
        popd
        pause
        exit /b 1
    )
)

:: 2. Activate Environment
if exist "py_lib\.venv\Scripts\activate.bat" (
    call "py_lib\.venv\Scripts\activate.bat"
) else (
    echo [ERROR] Virtual environment activation script missing!
    popd
    pause
    exit /b 1
)

:: Verify Python executable is functional inside the environment
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python executable not found in active environment.
    popd
    pause
    exit /b 1
)

:: Retain the current directory context for the core routing script
popd

:: 3. Forward parameters to the core routing script
python "%~dp0py_lib\main.py" %*

if %ERRORLEVEL% neq 0 (
    echo.
    echo [CRITICAL] Application execution failed with exit code %ERRORLEVEL%.
    echo.
    popd
    pause
    exit /b 1
)

exit /b 0
