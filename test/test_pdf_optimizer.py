# pylint: disable=redefined-outer-name
"""Automated verification suite for the PDF compression engine."""

from pathlib import Path
import fitz
import pytest
from pdf_optimizer import run, print_progress

# Resolve the absolute path to your physical test/data/sample.pdf file
SAMPLE_PDF_SRC = Path(__file__).parent / "data" / "sample.pdf"


@pytest.fixture
def sandbox_pdf(tmp_path):
    """Provides a fresh copy of sample.pdf inside an isolated system sandbox directory.

    This ensures tests don't modify or pollute your physical source repository.
    """
    if not SAMPLE_PDF_SRC.exists():
        pytest.fail(f"Testing aborted: Physical test asset missing at {SAMPLE_PDF_SRC}")

    input_file = tmp_path / "sample.pdf"
    input_file.write_bytes(SAMPLE_PDF_SRC.read_bytes())
    return input_file


def test_pdf_optimizer_completes_entire_cycle_successfully(sandbox_pdf):
    """Tests the complete end-to-end cycle: file generation, compression, and saving."""
    expected_output = sandbox_pdf.with_name("sample-compressed.pdf")

    # Run the ACTUAL source code directly with ZERO mocks
    run(pdf_path=str(sandbox_pdf))

    # 1. Verify filename construction and file writing logic worked on disk
    assert expected_output.exists()
    assert expected_output.stat().st_size > 0

    # 2. Verify compression layer integrity by checking if the output remains a valid PDF
    with fitz.open(expected_output) as compressed_doc:
        assert len(compressed_doc) > 0


def test_pdf_optimizer_throws_file_not_found_on_absent_target():
    """Asserts that running against an unverified path safely throws a FileNotFoundError."""
    with pytest.raises(FileNotFoundError, match="Target document absent"):
        run(pdf_path="missing_file.pdf")


def test_print_progress_outputs_clean_string_stream(capsys):
    """Verifies the text-based layout renders accurate progress updates to stdout streams."""
    print_progress(current=5, total=10, prefix="Testing")

    captured = capsys.readouterr().out
    assert "Testing" in captured
    assert "50.0%" in captured
    assert "###" in captured
