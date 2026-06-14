@echo off
SETLOCAL EnableExtensions
cls

echo ============================================================
echo         ISOLATED SANDBOX PRODUCTION BUILDER (DYNAMIC)
echo ============================================================
echo.

:: 1. Pre-Flight Workspace Safety Check
echo [1/5] Checking workspace integrity...
if exist src\.venv (
    echo [⚠️ WARNING] Found an accidental .venv folder inside the src directory!
    echo Removing the stray virtual environment before staging...
    rmdir /s /q src\.venv
    if errorlevel 1 (
        echo [❌ CRITICAL] Failed to clear the stray .venv from src. Close any open files and retry.
        goto BUILD_FAILED
    )
    echo [✓] Workspace cleared successfully.
) else (
    echo [✓] Workspace integrity verified. No stray environments found in src/.
)

:: 2. Reset and Stage inside the Build Directory
echo.
echo [2/5] Resetting build staging area...
if exist build rmdir /s /q build
mkdir build

echo Copying clean source code and requirements to build/src staging...
xcopy /s /e /y src build\src\ >nul

:: 3. Create the Temporary Sandbox Virtual Environment
echo.
echo [3/5] Creating a dedicated, isolated build environment...
py -m venv build\.build_venv
if errorlevel 1 (
    echo [❌ CRITICAL] Failed to create isolated virtual environment!
    goto BUILD_FAILED
)

:: 4. Activate and Hydrate the Build Environment
echo Activating clean sandbox environment...
call build\.build_venv\Scripts\activate.bat

echo Upgrading pipeline dependencies...
python -m pip install --upgrade pip --quiet
if not exist build\src\requirements.txt (
    echo [❌ CRITICAL] requirements.txt missing from src folder!
    goto BUILD_FAILED
)
pip install -r build\src\requirements.txt --quiet

:: We temporarily install pylint ONLY to the build sandbox to run code checks
pip install pylint --quiet

:: 5. Run Automated Testing Suite inside the Isolated Sandbox
echo.
echo [4/5] Launching code tests and syntax verification...
echo ------------------------------------------------------------

:: Test A: Check syntax across all staged files using compileall
python -m compileall -q build\src
if errorlevel 1 (
    echo [❌ CRITICAL] Syntax validation failed inside pristine environment!
    goto BUILD_FAILED
)

:: Test B: Execute Pylint against the isolated files
echo Running structural quality checks (Pylint)...
pylint build\src --disable=C0114,C0115,C0116
if errorlevel 1 (
    echo.
    echo [⚠️ WARNING] Pylint code standard checks did not pass perfectly.
    goto BUILD_FAILED
)

echo ------------------------------------------------------------
echo [✓] All validation tests completed successfully!

:: 6. Deploy to Production (Dist Folder)
echo.
echo [5/5] Deploying validated artifacts to production folder...
if exist dist rmdir /s /q dist
mkdir dist

xcopy /s /e /y build\src dist\ >nul

:: Deactivate and wipe the sandbox environment to leave the project folder clean
call deactivate
echo Cleaning up temporary sandbox environment files...
rmdir /s /q build\.build_venv

echo.
echo ============================================================
echo  🎉 BUILD SUCCESSFUL! Clean production files ready in \dist
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
echo  ❌ BUILD FAILED: Production artifacts were not generated.
echo ============================================================
echo.
pause
exit /b 1
