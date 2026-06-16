# pylint: disable=redefined-outer-name, duplicate-code
"""Automated verification suite for the subprocess tracking module."""

import sys
from unittest.mock import patch, MagicMock
import pytest
from cli_runner import run


@pytest.fixture
def mock_popen():
    """Provides a safely managed stub representation of a running process context."""
    with patch("subprocess.Popen") as mock_context:
        mock_process = MagicMock()
        mock_process.__enter__.return_value = mock_process
        mock_process.wait.return_value = 0
        mock_context.return_value = mock_process
        yield mock_context


def test_runner_preserves_raw_run_commands(mock_popen):
    """Ensures 'run' targets bypass local interpreter module injection."""
    run(tool_args=["git", "status"], mode="run")

    mock_popen.assert_called_once()
    called_args, called_kwargs = mock_popen.call_args
    assert called_args == (["git", "status"],)
    assert called_kwargs["stdout"] == sys.stdout


def test_runner_prepends_python_environment_flags(mock_popen):
    """Ensures 'py' targets receive clean virtual environment bindings."""
    run(tool_args=["pip", "--version"], mode="py")

    mock_popen.assert_called_once()
    called_args, _ = mock_popen.call_args
    assert called_args == ([sys.executable, "-m", "pip", "--version"],)


def test_runner_cleanses_duplicate_module_arguments(mock_popen):
    """Guarantees human entry typos like 'py python -m pip' heal themselves."""
    run(tool_args=["python", "-m", "pip", "install"], mode="py")

    mock_popen.assert_called_once()
    called_args, _ = mock_popen.call_args
    assert called_args == ([sys.executable, "-m", "pip", "install"],)


def test_runner_raises_value_error_on_empty_args():
    """Asserts that executing blank commands halts safely immediately."""
    with pytest.raises(ValueError, match="cannot be empty"):
        run(tool_args=[], mode="py")


def test_runner_raises_value_error_on_invalid_mode():
    """Asserts that passing unstructured engine targets triggers tracking blocks."""
    with pytest.raises(ValueError, match="Unsupported routing engine"):
        run(tool_args=["git"], mode="invalid_framework")
