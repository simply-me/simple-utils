"""Automated verification suite for the main application launcher router."""

import pathlib
import sys
from unittest.mock import patch

import pytest
from main import get_version, main


def test_router_forwards_run_mode_correctly() -> None:
    """Verifies that 'simply run' paths map correctly to the runner module."""
    test_arguments = ["run git status --verbose"]

    with patch("main.cli_runner.run", return_value=0) as mock_runner:
        with patch.object(sys, "argv", ["main.py"] + test_arguments):
            with pytest.raises(SystemExit) as exit_wrapper:
                main()

            assert exit_wrapper.value.code == 0
            mock_runner.assert_called_once_with(tool_args=["git", "status", "--verbose"], mode="run")


def test_router_handles_double_dash_separator() -> None:
    """Ensures argparse processes the double dash boundary according to POSIX rules."""
    test_arguments = ["run git -- status"]

    with patch("main.cli_runner.run", return_value=0) as mock_runner:
        with patch.object(sys, "argv", ["main.py"] + test_arguments):
            with pytest.raises(SystemExit):
                main()

            # Argparse natively consumes the '--' marker here, which is standard behavior
            mock_runner.assert_called_once_with(tool_args=["git", "status"], mode="run")


def test_router_rejects_unknown_modes(capsys: pytest.CaptureFixture[str]) -> None:
    """Verifies argparse cleanly blocks and flags invalid execution keywords."""
    test_arguments = ["invalid_mode git status"]

    with patch.object(sys, "argv", ["main.py"] + test_arguments):
        with pytest.raises(SystemExit) as exit_wrapper:
            main()

        assert exit_wrapper.value.code == 2
        assert "invalid choice" in capsys.readouterr().err


def test_router_handles_unpacked_multi_argument_fallback() -> None:
    """Covers line 50 fallback when arguments are already isolated as distinct items."""
    # Simulates bypassing the single packed macro string layout logic (len(raw_args) > 1)
    test_arguments = ["run", "git", "status"]

    with patch("main.cli_runner.run", return_value=0) as mock_runner:
        with patch.object(sys, "argv", ["main.py"] + test_arguments):
            with pytest.raises(SystemExit) as exit_wrapper:
                main()

            assert exit_wrapper.value.code == 0
            mock_runner.assert_called_once_with(tool_args=["git", "status"], mode="run")


def test_router_traps_defensive_empty_tokenization_failure(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Covers lines 35 & 38-39 by passing white spaces that shlex unpacks to an empty list."""
    test_arguments = ["   "]  # Splitting empty spacing results in token array length zero

    with patch.object(sys, "argv", ["main.py"] + test_arguments):
        with pytest.raises(SystemExit) as exit_wrapper:
            main()

        assert exit_wrapper.value.code == 2
        captured_error = capsys.readouterr().err
        assert "No execution parameters reached the core engine" in captured_error


def test_router_critical_exception_handling(capsys: pytest.CaptureFixture[str]) -> None:
    """Ensures unexpected runtime or execution crashes exit safely with status 1."""
    test_arguments = ["run broken_tool"]

    # Simulating a raw system exception (like an invalid memory or typing failure)
    with patch("main.cli_runner.run", side_effect=Exception("Severe system breakdown")):
        with patch.object(sys, "argv", ["main.py"] + test_arguments):
            with pytest.raises(SystemExit) as exit_wrapper:
                main()

            assert exit_wrapper.value.code == 1
            captured_error = capsys.readouterr().err
            # Asserts that the system prints our lean error message format
            assert "CRITICAL ROUTER ERROR" in captured_error


def test_router_successful_intercept_bypass() -> None:
    """Verifies intercepts completely bypass the runner module on True matches."""
    # This mimics a packed string coming from the Windows launcher wrapper
    test_arguments = ["py custom_intercepted_tool --flag"]

    with patch("main.intercepts.handle_custom_intercept", return_value=True) as mock_intercept:
        with patch("main.cli_runner.run") as mock_runner:
            with patch.object(sys, "argv", ["main.py"] + test_arguments):
                with pytest.raises(SystemExit) as exit_wrapper:
                    main()

                # Confirms it enters the True condition (Line 50) and exits cleanly
                assert exit_wrapper.value.code == 0
                mock_intercept.assert_called_once_with(target="custom_intercepted_tool", forwarded_args=["--flag"])
                mock_runner.assert_not_called()


# ==============================================================================
# NEW: COMMITIZEN VERSION FILE TESTING COVERAGE
# ==============================================================================
def test_get_version_reads_file_successfully(tmp_path, monkeypatch) -> None:
    """Verifies get_version accurately reads and strips the plain text version file."""
    # Create an artificial version file inside a temporary test workspace
    mock_version_file = tmp_path / "version"
    mock_version_file.write_text("  2.4.1\n", encoding="utf-8")

    # Point pathlib.Path.parent / "version" to our temporary test file
    monkeypatch.setattr(pathlib.Path, "parent", tmp_path)

    extracted_version = get_version()
    # Confirms whitespace stripping rules evaluate correctly
    assert extracted_version == "2.4.1"


def test_get_version_graceful_fallback_on_missing_file(monkeypatch) -> None:
    """Ensures get_version intercepts missing files or exceptions without crashing."""
    # Point the parent locator path to a non-existent dummy file to trigger the except clause
    ghost_path = pathlib.Path("ghost_folder/absent_target")
    monkeypatch.setattr(pathlib.Path, "parent", ghost_path)

    extracted_version = get_version()
    # Confirms it safely delivers your development fallback string token
    assert extracted_version == "no-version"
