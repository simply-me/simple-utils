@echo off
SETLOCAL EnableExtensions

:: 1. Argument Check (Catches completely empty user attempts)
if "%~1"=="" (
    echo [ERROR] No arguments provided. This script requires at least one argument.
    echo Usage: %~nx0 [arguments...]

    :: Only pause if the user double-clicked the file from the Windows GUI
    echo %cmdcmdline% | findstr /i /c:"%~nx0" >nul && pause
    exit /b 1
)

:: Secure the working directory relative to this script
pushd "%~dp0"

:: 2. Auto-Bootstrap Check
if not exist "py_lib\.venv" (
    echo [Launcher] Environment missing. Initializing production setup...
    if exist "simply-env.cmd" (
        call "simply-env.cmd"
    ) else (
        echo [ERROR] simply-env.cmd is missing from src folder! Cannot initialize.
        popd
        pause
        exit /b 1
    )
)

:: 3. Activate Environment
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

:: 4. Forward parameters to the core routing script as a single, un-mutated string block
python "%~dp0py_lib\main.py" "%*"

:: Capture the exact code emitted by the python layer
SET EXIT_STATUS=%ERRORLEVEL%

:: Only pause if there was an actual crash inside the wrapper itself before running python.
:: Otherwise, pass the downstream tool's error level right back to the console window.
exit /b %EXIT_STATUS%
