#!/usr/bin/env bash

# Exit immediately if a command fails, or if an uninitialized variable is used
set -euo pipefail

clear
echo "============================================================"
echo "                   Build in Progress"
echo "============================================================"
echo

# Reset and Stage inside the Build Directory
echo
echo "Resetting build staging area..."
rm -rf build
mkdir -p build/src

echo "Copying source code and requirements to build/src staging..."
cp -r src/* build/src/
find build/src/ -type d \( -name "__pycache__" -o -name ".venv" -o -name "venv" -o -name ".git" \) -exec rm -rf {} + 2>/dev/null || true
find build/src/ -type f -name "*.pyc" -delete 2>/dev/null || true

# Create the Temporary Sandbox Virtual Environment
echo
echo "Creating isolated build environment..."
python -m venv build/.build_venv || {
    echo "[CRITICAL] Failed to create isolated virtual environment!"
    exit 1
}

# Activation and Hydrate the Build Environment
echo
echo "Activating clean sandbox environment..."
# Disable unbound variable checking temporarily.
# Virtualenv activation scripts natively use uninitialized variables which crashes 'set -u'.
set +u
# shellcheck disable=SC1091
source build/.build_venv/Scripts/activate
set -u

echo "Upgrading pipeline dependencies..."
python -m pip install --upgrade pip --quiet
if [ ! -f "build/src/py_lib/requirements.txt" ]; then
    echo "[CRITICAL] requirements.txt missing from src/py_lib folder!"
    deactivate 2>/dev/null || true
    exit 1
fi
pip install -r build/src/py_lib/requirements.txt --quiet

# Temporarily install validation tools to the sandbox
echo "Installing verification and analysis framework dependencies..."
pip install pylint pytest pytest-cov mypy --quiet

# Run Automated Testing Suite inside the Isolated Sandbox
echo
echo "Launching code tests and syntax verification..."
echo "------------------------------------------------------------"

# Check syntax across all staged files using compileall
echo "Checking fundamental syntax (Compileall)..."
python -m compileall -q build/src/py_lib || {
    echo "[CRITICAL] Syntax validation failed inside pristine environment!"
    deactivate 2>/dev/null || true
    exit 1
}
echo "-> Syntax validation successful."
echo

# Run Pylint Check
echo "------------------------------------------------------------"
echo "Running structural quality checks (Pylint)..."
echo "------------------------------------------------------------"
# Initializing variable and safely wrapping execution to prevent 'set -e' from halting early
PYLINT_ERROR=0
python -m pylint src/py_lib test/ --rcfile=.pylintrc --output-format=colorized || PYLINT_ERROR=$?

# Bitmask: 1 (Fatal) + 2 (Error) + 32 (Config Error) = 35
HARD_FAILURES=$(( PYLINT_ERROR & 35 ))

if [ "$HARD_FAILURES" -gt 0 ]; then
    echo
    echo "[CRITICAL] Pylint detected blocking Errors or Fatal syntax crashes!"
    echo "Please fix all actual Errors before attempting to build."
    deactivate 2>/dev/null || true
    exit 1
fi

# If exit code > 0 but no hard failures, only Warnings/Refactors exist
if [ "$PYLINT_ERROR" -gt 0 ]; then
    echo
    echo "[WARNING] Pylint detected code style warnings/refactor suggestions."

    # Prompt user interactively (Y/N)
    read -r -p "Would you like to bypass these style warnings and complete the deployment anyway? (y/n): " CHOICE
    case "$CHOICE" in
        [yY][eE][sS]|[yY])
            echo "Bypassing warnings. Proceeding to type validation..."
            echo
            ;;
        *)
            echo "Deployment aborted by user."
            deactivate 2>/dev/null || true
            exit 1
            ;;
    esac
else
    echo "-> Code style and structural checks successful."
    echo
fi

# Run Mypy Check
echo "------------------------------------------------------------"
echo "Running strict type layout verification (Mypy)..."
echo "------------------------------------------------------------"
# Initializing variable and safely wrapping execution to prevent 'set -e' from halting early
MYPY_ERROR=0
python -m mypy src/py_lib/ --ignore-missing-imports || MYPY_ERROR=$?

if [ "$MYPY_ERROR" -gt 0 ]; then
    echo
    echo "[CRITICAL] Mypy detected strict type inconsistencies or logical data mismatches!"
    deactivate 2>/dev/null || true
    exit 1
fi
echo "-> Type layout verification successful."
echo

# Run Pytest Check
echo "------------------------------------------------------------"
echo "Running automated unit tests and tracking coverage (Pytest)..."
echo "------------------------------------------------------------"
python -m pytest || {
    echo
    echo "[CRITICAL] Automated unit tests failed inside pristine sandbox!"
    deactivate 2>/dev/null || true
    exit 1
}

echo "------------------------------------------------------------"
echo "[✓] All validation tests completed successfully!"

# Deploy to Production (Dist Folder)
echo
echo "Deploying validated artifacts to production folder..."
rm -rf dist
mkdir -p dist/simple-utils

# Replaced rsync: Copy to production destination and strip compileall cache targets
cp -r build/src/* dist/simple-utils/
find dist/simple-utils/ -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find dist/simple-utils/ -type f -name "*.pyc" -delete 2>/dev/null || true

# Package the application into a zip file using native Python shutil
echo "Packaging simple-utils into a compressed zip file..."
(
    cd dist
    python -c "import shutil; shutil.make_archive('simple-utils', 'zip', 'simple-utils')" || {
        echo "[CRITICAL] Failed to create compressed zip archive!"
        exit 1
    }
)

# Deactivate and wipe sandbox environment
set +u
deactivate 2>/dev/null || true
set -u

echo "Cleaning up temporary sandbox environment files..."
rm -rf build/.build_venv

echo
echo "============================================================"
echo " BUILD SUCCESSFUL! Clean production zip ready in dist/simple-utils.zip"
echo "============================================================"
echo
exit 0
