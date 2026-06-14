@echo off
SETLOCAL EnableExtensions

:: Create the development venv at the project root level
if not exist .venv (
    echo Creating development virtual environment...
    py -m venv .venv
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
