# pylint: disable=redefined-outer-name
"""Integration test suite targeting the Windows batch launcher wrapper."""

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
def cmd_file_path() -> str:
    """Dynamically resolves the path to simply.cmd based on PYTHONPATH."""
    # Catches local build.sh runs and GitHub Actions env
    if "build" in os.environ.get("PYTHONPATH", ""):
        return os.path.join("build", "src", "simply.cmd")

    return os.path.join("src", "simply.cmd")


def test_cmd_script_exits_one_on_empty_arguments(workspace_root: str, cmd_file_path: str) -> None:
    """Ensures simply.cmd blocks empty parameters and exits with error code 1."""
    result = subprocess.run(
        [cmd_file_path],
        capture_output=True,
        text=True,
        shell=True,
        check=False,
        cwd=workspace_root,
    )
    assert result.returncode == 1

    combined_output = result.stdout + result.stderr
    assert "[ERROR] No arguments provided" in combined_output or "ERROR: Invalid arguments provided" in combined_output


def test_cmd_script_forwards_arguments_safely(workspace_root: str, cmd_file_path: str) -> None:
    """Ensures the wrapper passes arguments through cleanly to the routing layer."""
    result = subprocess.run(
        [cmd_file_path, "invalid_mode", "git", "status"],
        capture_output=True,
        text=True,
        shell=True,
        check=False,
        cwd=workspace_root,
    )

    assert result.returncode in (1, 2)

    combined_output = result.stdout + result.stderr
    assert "invalid choice: 'invalid_mode'" in combined_output or "ERROR: Invalid arguments provided" in combined_output
