@echo off
SETLOCAL EnableExtensions

:: Create a clean venv in the py_lib subfolder under this folder
echo Creating clean virtual environment...
py -m venv --clear "%~dp0py_lib\.venv"
if errorlevel 1 (
    echo [CRITICAL] Failed to create clean virtual environment!
    pause
    exit /b 1
)

:: Activate the local deployment venv
call "%~dp0py_lib\.venv\Scripts\activate.bat"
python -m pip install --upgrade pip --quiet

:: Install from requirements.txt in the same folder
if exist "%~dp0py_lib\requirements.txt" (
    echo Installing production dependencies...
    pip install -r "%~dp0py_lib\requirements.txt"
) else (
    echo ERROR: requirements.txt not found!
    pause
    exit /b 1
)

echo CONFIGURATION COMPLETE: Simple Utils runtime environment is ready.
pause
