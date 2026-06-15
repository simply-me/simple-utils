@echo off
SETLOCAL EnableExtensions

:: Create a clean development venv at the project root level
echo Creating clean development virtual environment...
py -m venv --clear.venv
if errorlevel 1 (
    echo [CRITICAL] Failed to create clean development virtual environment!
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat
python -m pip install --upgrade pip --quiet

:: Install dev dependencies (which link directly down to src/requirements.txt)
if exist requirements-dev.txt (
    pip install -r requirements-dev.txt
)

:: Initialize Git hooks if repository exists
if exist .git (
    pre-commit install
)

echo Workspace development environment armed and ready.
pause
