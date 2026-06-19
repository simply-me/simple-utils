# pylint: disable=redefined-outer-name,duplicate-code
"""Automated verification suite for the PDF compression engine."""

from pathlib import Path

import pytest
from pdf_optimizer import print_progress, run

# Resolve absolute paths to your physical test data assets
DATA_DIR = Path(__file__).parent / "data"
UNCOMPRESSED_SRC = DATA_DIR / "uncompressed.pdf"
COMPRESSED_SRC = DATA_DIR / "compressed.pdf"


@pytest.fixture
def sandbox_uncompressed_pdf(tmp_path: Path) -> Path:
    """Provides a fresh copy of uncompressed.pdf inside an isolated system sandbox."""
    if not UNCOMPRESSED_SRC.exists():
        pytest.fail(f"Testing aborted: Missing source asset at {UNCOMPRESSED_SRC}")

    input_file = tmp_path / "uncompressed.pdf"
    input_file.write_bytes(UNCOMPRESSED_SRC.read_bytes())
    return input_file


@pytest.fixture
def sandbox_compressed_pdf(tmp_path: Path) -> Path:
    """Provides a fresh copy of compressed.pdf inside an isolated system sandbox."""
    if not COMPRESSED_SRC.exists():
        pytest.fail(f"Testing aborted: Missing source asset at {COMPRESSED_SRC}")

    input_file = tmp_path / "compressed.pdf"
    input_file.write_bytes(COMPRESSED_SRC.read_bytes())
    return input_file


def test_pdf_optimizer_compresses_heavy_file_successfully(
    sandbox_uncompressed_pdf: Path,
) -> None:
    """Guarantees that an unoptimized high-DPI PDF is successfully downscaled and saved."""
    orig_size = sandbox_uncompressed_pdf.stat().st_size

    # Run the optimization engine on the raw, heavy file copy
    run(pdf_path=str(sandbox_uncompressed_pdf))

    output_dir = sandbox_uncompressed_pdf.parent
    generated_files = list(output_dir.glob("uncompressed-compressed*.pdf"))

    assert len(generated_files) > 0
    target_output = generated_files[0]

    assert target_output.exists()
    assert target_output.stat().st_size > 0
    # Confirm that the file size was successfully reduced
    assert target_output.stat().st_size < orig_size


def test_pdf_optimizer_processes_already_optimized_file_gracefully(
    sandbox_compressed_pdf: Path,
) -> None:
    """Verifies that running on an already optimized file finishes cleanly without errors."""
    # Run tool on the pre-optimized file. It should execute completely without a guard exit.
    run(pdf_path=str(sandbox_compressed_pdf))

    output_dir = sandbox_compressed_pdf.parent
    generated_files = list(output_dir.glob("compressed-compressed*.pdf"))

    # UPDATED: Assert that an output file is created successfully
    assert len(generated_files) > 0
    target_output = generated_files[0]
    assert target_output.exists()
    assert target_output.stat().st_size > 0


def test_pdf_optimizer_throws_file_not_found_on_absent_target() -> None:
    """Asserts that running against an unverified path safely throws a FileNotFoundError."""
    with pytest.raises(FileNotFoundError, match="Target document absent"):
        run(pdf_path="missing_file.pdf")


def test_print_progress_outputs_clean_string_stream(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Verifies the text-based layout renders accurate progress updates to stdout streams."""
    print_progress(current=5, total=10, prefix="Testing")

    captured = capsys.readouterr().out
    assert "Testing" in captured
    assert "50.0%" in captured
    assert "###" in captured
