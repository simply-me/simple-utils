# pylint: disable=redefined-outer-name
"""Automated verification suite for the custom registry intercept router."""

from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
from intercepts import handle_custom_intercept, route_pdf_compress

# Standard test asset tracking string
SAMPLE_PDF = str(Path(__file__).parent / "data" / "sample.pdf")


def test_handle_custom_intercept_returns_false_on_unknown_target():
    """Ensures unrecognized tools gracefully drop straight out of the intercept check."""
    result = handle_custom_intercept(target="unknown-tool", forwarded_args=[])
    assert result is False


def test_handle_custom_intercept_routes_valid_target():
    """Ensures registered tools match successfully and fire their routed function wrappers."""
    args = ["--input", SAMPLE_PDF]
    mock_route = MagicMock()

    with patch("intercepts.CUSTOM_INTERCEPTS", {"pdf-compress": mock_route}):
        result = handle_custom_intercept(target="pdf-compress", forwarded_args=args)

        assert result is True
        mock_route.assert_called_once_with(args)


@patch("pdf_optimizer.run")
def test_route_pdf_compress_passes_clean_arguments(mock_optimizer_run):
    """Ensures argparse successfully extracts structural input flags and passes them to the engine."""
    route_pdf_compress(["--input", SAMPLE_PDF])
    mock_optimizer_run.assert_called_once_with(pdf_path=SAMPLE_PDF)


def test_route_pdf_compress_raises_system_exit_on_missing_required_flag():
    """Ensures argparse cleanly raises SystemExit if the required --input flag is omitted."""
    with pytest.raises(SystemExit):
        route_pdf_compress([])
