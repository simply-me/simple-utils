@echo off
SETLOCAL EnableExtensions
cls

echo ============================================================
echo                    Build in Progress
echo ============================================================
echo.

:: 1. Reset and Stage inside the Build Directory
echo.
echo [1] Resetting build staging area...
if exist build rmdir /s /q build
mkdir build

echo Copying source code and requirements to build/src staging...
:: Mirror src into build\src, ignoring local caches
robocopy src build\src /e /xd __pycache__ .venv venv .git /xf *.pyc >nul

:: 2. Create the Temporary Sandbox Virtual Environment
echo.
echo [2] Creating isolated build environment...
py -m venv build\.build_venv
if errorlevel 1 (
    echo [CRITICAL] Failed to create isolated virtual environment!
    goto BUILD_FAILED
)

:: 3. Activate and Hydrate the Build Environment
echo [3] Activating clean sandbox environment...
call build\.build_venv\Scripts\activate.bat

echo Upgrading pipeline dependencies...
python -m pip install --upgrade pip --quiet
if not exist build\src\py_lib\requirements.txt (
    echo [CRITICAL] requirements.txt missing from src\py_lib folder!
    goto BUILD_FAILED
)
pip install -r build\src\py_lib\requirements.txt --quiet

:: We temporarily install pylint ONLY to the build sandbox to run code checks
pip install pylint --quiet

:: 4. Run Automated Testing Suite inside the Isolated Sandbox
echo.
echo [4] Launching code tests and syntax verification...
echo ------------------------------------------------------------

:: Test A: Check syntax across all staged files using compileall
python -m compileall -q build\src\py_lib
if errorlevel 1 (
    echo [CRITICAL] Syntax validation failed inside pristine environment!
    goto BUILD_FAILED
)

echo Running structural quality checks (Pylint)...
:: Explicitly setting PYTHONPATH to the original directory for correct workspace import mapping
set PYTHONPATH=%CD%\src\py_lib

:: Run Pylint on your original source files. Links are 100% clickable!
python -m pylint src\py_lib --disable=C0111,W0511,R0903,C0103,R0913,R0914
set PYLINT_ERROR=%errorlevel%

:: Clean up the temporary environment variable
set PYTHONPATH=

:: Bitmask: 1 (Fatal) + 2 (Error) + 32 (Config Error) = 35
:: If any of these bits are flipped, the code contains actual bugs or broken syntax
set /a HARD_FAILURES="%PYLINT_ERROR% & 35"

if %HARD_FAILURES% gtr 0 (
    echo.
    echo [CRITICAL] Pylint detected blocking Errors or Fatal syntax crashes!
    echo Please fix all actual Errors before attempting to build.
    goto BUILD_FAILED
)

:: If the exit code is still greater than 0, it means ONLY Warnings/Refactors exist
if %PYLINT_ERROR% gtr 0 (
    echo.
    echo [WARNING] Pylint detected code style warnings/refactor suggestions.

    :: Prompt the user for an interactive choice (Y/N)
    choice /c YN /m "Would you like to bypass these style warnings and complete the deployment anyway"
    if errorlevel 2 (
        echo Deployment aborted by user.
        goto BUILD_FAILED
    )
    echo Bypassing warnings. Proceeding to deployment...
)

echo ------------------------------------------------------------
echo [✓] All validation tests completed successfully!

:: 6. Deploy to Production (Dist Folder)
echo.
echo [5/5] Deploying validated artifacts to production folder...
if exist dist rmdir /s /q dist
mkdir dist

:: ROBOCOPY: Excludes the __pycache__ folders compileall generated inside build\src
robocopy build\src dist\simple-utils /e /xd __pycache__ /xf *.pyc >nul
:: TODO: create version file in dist

:: Deactivate and wipe the sandbox environment to leave the project folder clean
call deactivate
echo Cleaning up temporary sandbox environment files...
rmdir /s /q build\.build_venv

echo.
echo ============================================================
echo  BUILD SUCCESSFUL! Clean production files ready in \dist
echo ============================================================
echo.
pause
exit /b 0

:BUILD_FAILED
:: Ensure we deactivate if something crashed while the sandbox venv was active
if "%VIRTUAL_ENV%"=="" (goto SKIP_DEACTIVATE)
call deactivate
:SKIP_DEACTIVATE
echo.
echo ============================================================
echo  BUILD FAILED: Production artifacts were not generated.
echo ============================================================
echo.
pause
exit /b 1
