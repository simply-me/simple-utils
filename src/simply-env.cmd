@echo off
SETLOCAL EnableExtensions

:: Set paths
SET "VENV_DIR=%~dp0py_lib\.venv"
SET "REQ_FILE=%~dp0py_lib\requirements.txt"

:: Initialize mode flag
SET "IS_UPDATE=0"

:: Check if ANY argument was provided
IF "%~1"=="" GOTO :DEFAULT_MODE

:: Strict argument checking (Only --update is allowed)
IF /I "%~1"=="--update" (
    :: Check no second argument was passed
    IF NOT "%~2"=="" GOTO :SHOW_USAGE
    SET "IS_UPDATE=1"
    GOTO :UPDATE_MODE
)
:: Invalid argument passed
GOTO :SHOW_USAGE


:SHOW_USAGE
echo =======================================================================
echo ERROR: Invalid arguments provided.
echo =======================================================================
echo Usage:
echo   %~nx0          - Performs a clean environment setup.
echo   %~nx0 --update - Updates packages in the existing environment.
echo =======================================================================
PAUSE
EXIT /B 1


:DEFAULT_MODE
:: Create a clean venv in the py_lib subfolder under this folder
echo Creating clean environment...
py -m venv --clear "%VENV_DIR%"
IF ERRORLEVEL 1 (
    echo [CRITICAL] Failed to create clean environment!
    PAUSE
    EXIT /B 1
)
GOTO :ACTIVATE_VENV


:UPDATE_MODE
:: Ensure the venv actually exists before trying to update it
IF NOT EXIST "%VENV_DIR%\Scripts\activate.bat" (
    echo [ERROR] No existing environment found to update!
    echo.
    GOTO :DEFAULT_MODE
)
echo [UPDATE MODE] Updating existing packages...
GOTO :ACTIVATE_VENV


:ACTIVATE_VENV
:: Activate the local deployment venv
CALL "%VENV_DIR%\Scripts\activate.bat"
python -m pip install --upgrade pip --quiet

:: Install/Update from requirements.txt in the same folder
IF EXIST "%REQ_FILE%" (
    echo Syncing/Installing production dependencies...
    pip install -r "%REQ_FILE%" --upgrade
) ELSE (
    echo ERROR: requirements.txt not found at: %REQ_FILE%
    PAUSE
    EXIT /B 1
)

echo CONFIGURATION COMPLETE: Simple Utils runtime environment is ready.
PAUSE
