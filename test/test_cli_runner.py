# pylint: disable=redefined-outer-name, duplicate-code
"""Automated verification suite for the subprocess tracking module."""

import subprocess
import sys
from typing import Generator  # FIXED: Imported Generator to resolve F821
from unittest.mock import MagicMock, patch

import pytest
from cli_runner import run


@pytest.fixture
def mock_popen() -> Generator[MagicMock, None, None]:
    """Provides a safely managed stub representation of a running process context."""
    with patch("subprocess.Popen") as mock_context:
        mock_process = MagicMock()
        mock_process.__enter__.return_value = mock_process
        mock_process.wait.return_value = 0
        mock_context.return_value = mock_process
        yield mock_context


def test_runner_preserves_raw_run_commands(mock_popen: MagicMock) -> None:
    """Ensures 'run' targets bypass local interpreter module injection."""
    run(tool_args=["git", "status"], mode="run")

    mock_popen.assert_called_once()
    called_args, called_kwargs = mock_popen.call_args
    assert called_args == (["git", "status"],)
    assert called_kwargs["stdout"] == sys.stdout


def test_runner_prepends_python_environment_flags(mock_popen: MagicMock) -> None:
    """Ensures 'py' targets receive clean virtual environment bindings."""
    run(tool_args=["pip", "--version"], mode="py")

    mock_popen.assert_called_once()
    called_args, _ = mock_popen.call_args
    assert called_args == ([sys.executable, "-m", "pip", "--version"],)


def test_runner_cleanses_duplicate_module_arguments(mock_popen: MagicMock) -> None:
    """Guarantees human entry typos like 'py python -m pip' heal themselves."""
    run(tool_args=["python", "-m", "pip", "install"], mode="py")

    mock_popen.assert_called_once()
    called_args, _ = mock_popen.call_args
    assert called_args == ([sys.executable, "-m", "pip", "install"],)


def test_runner_raises_value_error_on_empty_args() -> None:
    """Asserts that executing blank commands halts safely immediately."""
    with pytest.raises(ValueError, match="cannot be empty"):
        run(tool_args=[], mode="py")


def test_runner_raises_value_error_on_invalid_mode() -> None:
    """Asserts that passing unstructured engine targets triggers tracking blocks."""
    with pytest.raises(ValueError, match="Unsupported routing engine"):
        run(tool_args=["git"], mode="invalid_framework")


def test_runner_raises_error_on_non_existent_executable(mock_popen: MagicMock) -> None:
    """Verifies that running a non-existent binary raises a FileNotFoundError."""
    # Simulate the OS throwing the missing file error
    mock_popen.side_effect = FileNotFoundError(
        "[WinError 2] The system cannot find the file specified"
    )

    # Assert that the application properly bubbles up or re-raises the exception
    with pytest.raises(FileNotFoundError):
        run(tool_args=["nosuchfile"], mode="run")


def test_runner_triggers_failed_returncode_branch(mock_popen: MagicMock) -> None:
    """Forces execution into the 'if returncode != 0' block to verify error handling."""
    # 1. Arrange: Force the mocked process to return a non-zero exit status (e.g., 1)
    mock_process = mock_popen.return_value.__enter__.return_value
    mock_process.wait.return_value = 1

    # 2. Act & Assert: Verify it enters the branch and raises CalledProcessError
    with pytest.raises(subprocess.CalledProcessError) as exc_info:
        run(tool_args=["git", "status"], mode="run")

    # 3. Verify the exception object holds the exact failure metadata from that block
    assert exc_info.value.returncode == 1
    assert exc_info.value.cmd == ["git", "status"]
