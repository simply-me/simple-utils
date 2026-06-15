# pylint: disable=duplicate-code
"""Automated verification suite for the main application launcher router."""

import sys
from unittest.mock import patch
import pytest

from main import main


def test_router_forwards_run_mode_correctly():
    """Verifies that 'simply run' paths map correctly to the runner module."""
    test_arguments = ["simply", "run", "git", "status", "--verbose"]

    with patch("main.cli_runner.run", return_value=0) as mock_runner:
        with patch.object(sys, "argv", test_arguments):
            with pytest.raises(SystemExit) as exit_wrapper:
                main()

            assert exit_wrapper.value.code == 0
            mock_runner.assert_called_once_with(
                tool_args=["git", "status", "--verbose"], mode="run"
            )


def test_router_forwards_py_mode_correctly():
    """Verifies that 'simply py' paths map correctly to the runner module."""
    test_arguments = ["simply", "py", "pymupdf", "--input", "doc.pdf"]

    with patch("main.cli_runner.run", return_value=0) as mock_runner:
        with patch.object(sys, "argv", test_arguments):
            with pytest.raises(SystemExit) as exit_wrapper:
                main()

            assert exit_wrapper.value.code == 0
            mock_runner.assert_called_once_with(
                tool_args=["pymupdf", "--input", "doc.pdf"], mode="py"
            )


def test_router_strips_double_dash_separator():
    """Ensures downstream '--' barriers are safely popped before process execution."""
    test_arguments = ["simply", "run", "git", "--", "status"]

    with patch("main.cli_runner.run", return_value=0) as mock_runner:
        with patch.object(sys, "argv", test_arguments):
            with pytest.raises(SystemExit):
                main()

            mock_runner.assert_called_once_with(tool_args=["git", "status"], mode="run")


def test_router_rejects_unknown_modes(capsys):
    """Verifies argparse cleanly blocks and flags invalid execution keywords."""
    test_arguments = ["simply", "invalid_mode", "git", "status"]

    with patch.object(sys, "argv", test_arguments):
        with pytest.raises(SystemExit) as exit_wrapper:
            main()

        assert exit_wrapper.value.code == 2
        captured_error = capsys.readouterr().err
        assert "invalid choice" in captured_error
