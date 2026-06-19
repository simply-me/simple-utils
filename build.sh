#!/usr/bin/env bash

# Exit immediately if a command fails, or if an uninitialized variable is used
set -euo pipefail

clear
echo "============================================================"
echo "          Strategy A Build in Progress (Ruff + Mypy)"
echo "============================================================"
echo

# Reset and Stage inside the Build Directory
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
pip install ruff pytest pytest-cov mypy --quiet

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

# Run Ruff Check and Format Verification
echo "------------------------------------------------------------"
echo "Running static checks and style verification (Ruff)..."
echo "------------------------------------------------------------"
ruff check build/src/py_lib || {
    echo "[CRITICAL] Ruff linting validation failed!"
    deactivate 2>/dev/null || true
    exit 1
}
ruff format --check build/src/py_lib || {
    echo "[CRITICAL] Ruff formatting validation failed! Run 'ruff format' locally."
    deactivate 2>/dev/null || true
    exit 1
}
echo "-> Code quality and layout checks successful."
echo

# Run Mypy Check
echo "------------------------------------------------------------"
echo "Running strict type layout verification (Mypy)..."
echo "------------------------------------------------------------"
# Pointed safely to check the staging directory targets
MYPY_ERROR=0
python -m mypy build/src/py_lib/ || MYPY_ERROR=$?

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
export PYTHONPATH="build/src"
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

# Copy to production destination and strip compileall cache targets
cp -r build/src/* dist/simple-utils/

# Package your local Commitizen changelog documentation inside the zip
cp -f CHANGELOG.md dist/simple-utils/ 2>/dev/null || true

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
