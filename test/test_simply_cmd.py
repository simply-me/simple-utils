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
    # From /test/test_simply_cmd.py, going up one directory level hits the root /
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def test_cmd_script_exits_one_on_empty_arguments(workspace_root: str) -> None:
    """Ensures simply.cmd blocks empty parameters and exits with error code 1."""
    cmd_file = os.path.join("src", "simply.cmd")
    result = subprocess.run(
        [cmd_file],
        capture_output=True,
        text=True,
        shell=True,
        check=False,
        cwd=workspace_root,
    )
    assert result.returncode == 1
    assert "[ERROR] No arguments provided" in result.stdout


def test_cmd_script_forwards_arguments_safely(workspace_root: str) -> None:
    """Ensures the wrapper passes arguments through cleanly to the routing layer."""
    cmd_file = os.path.join("src", "simply.cmd")

    result = subprocess.run(
        [cmd_file, "invalid_mode", "git", "status"],
        capture_output=True,
        text=True,
        shell=True,
        check=False,
        cwd=workspace_root,  # Forces execution context directly from project root
    )

    # Argparse natively triggers exit code 2 when a choice is invalid
    assert result.returncode == 2

    combined_output = result.stdout + result.stderr
    assert "invalid choice: 'invalid_mode'" in combined_output
