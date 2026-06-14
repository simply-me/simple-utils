@echo off
SETLOCAL EnableExtensions

:: Create the venv in a subfolder right next to this script
if not exist "%~dp0.venv" (
    echo Creating production virtual environment...
    py -m venv "%~dp0.venv"
)

:: Activate the local deployment venv
call "%~dp0.venv\Scripts\activate.bat"
python -m pip install --upgrade pip --quiet

:: Install from requirements.txt in the same folder
if exist "%~dp0requirements.txt" (
    echo Installing production dependencies...
    pip install -r "%~dp0requirements.txt"
) else (
    echo ERROR: requirements.txt not found!
    pause
    exit /b 1
)

echo CONFIGURATION COMPLETE: Production runtime environment is ready.
pause
