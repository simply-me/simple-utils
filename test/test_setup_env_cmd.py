# pylint: disable=redefined-outer-name
"""Integration test suite targeting the environment setup batch script wrapper."""

import os
import subprocess
import sys

import pytest

if sys.platform != "win32":
    pytest.skip(
        "Skipping Windows CMD script tests on non-Windows platforms.",
        allow_module_level=True,
    )


@pytest.fixture
def workspace_root() -> str:
    """Returns the absolute path to the project root directory."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture
def setup_script_path() -> str:
    """Dynamically resolves the path to the environment setup script based on PYTHONPATH."""
    # Matches the exact approach used across your other integration tests
    if "build" in os.environ.get("PYTHONPATH", ""):
        return os.path.join("build", "src", "simply-env.cmd")  # Adjust filename if yours is .bat

    return os.path.join("src", "simply-env.cmd")


def test_setup_script_fails_on_invalid_arguments(workspace_root: str, setup_script_path: str) -> None:
    """Ensures the environment script blocks bad arguments and displays the correct usage menu."""
    result = subprocess.run(
        [setup_script_path, "--invalid-flag"],
        capture_output=True,
        text=True,
        shell=True,
        check=False,
        cwd=workspace_root,
    )
    # The usage block sets ERRORLEVEL 1 and calls EXIT /B 1
    assert result.returncode == 1

    combined_output = result.stdout + result.stderr
    assert "ERROR: Invalid arguments provided." in combined_output
    assert "Usage:" in combined_output


def test_setup_script_update_mode_triggers_correctly(workspace_root: str, setup_script_path: str) -> None:
    """Ensures that the --update flag skips clean installations and targets package updating."""
    result = subprocess.run(
        [setup_script_path, "--update"],
        capture_output=True,
        text=True,
        shell=True,
        check=False,
        cwd=workspace_root,
    )
    combined_output = result.stdout + result.stderr

    # Robust checking logic handles clean build fallback vs pre-existing venv update loops
    if "No existing environment found to update!" in combined_output:
        assert "[ERROR] No existing environment found to update!" in combined_output
        assert "Creating clean environment..." in combined_output
    else:
        assert "[UPDATE MODE] Updating existing packages..." in combined_output
        assert "Syncing/Installing production dependencies..." in combined_output
