import shutil
from pathlib import Path

import pytest
from pdf_optimizer import print_progress, run


# ==============================================================================
# PROGRESS BAR VISUALIZATION PASS
# ==============================================================================
def test_print_progress_live(capsys):
    """Executes the exact string formatter module against real screen logs."""
    print_progress(3, 5, prefix="Live Engine")
    captured = capsys.readouterr()

    assert "Live Engine: |" in captured.out
    assert "60.0%" in captured.out
    assert "(3/5 pages)" in captured.out


# ==============================================================================
# MISSING FILE CRASH EXCEPTION PASS
# ==============================================================================
def test_run_raises_real_file_not_found():
    """Confirms the production FileNotFoundError string logic triggers on raw files."""
    with pytest.raises(FileNotFoundError) as exc_info:
        run("test/data/ghost_document_file_target.pdf")

    assert "Target document absent" in str(exc_info.value)


# ==============================================================================
# END-TO-END EXECUTION & PATH COLLISION PASS
# ==============================================================================
def test_run_end_to_end_with_naming_collision_resolution(tmp_path):
    """Executes compression on your real uncompressed asset and tests the naming loop."""
    test_root = Path(__file__).parent
    real_source = test_root / "data" / "uncompressed.pdf"

    if not real_source.exists():
        pytest.fail(f"Required testing asset missing at path: {real_source}")

    # Copy your real uncompressed file into the temporary test workspace
    sandbox_input = tmp_path / "sample.pdf"
    shutil.copy(real_source, sandbox_input)

    # FORCE NAMING COLLISION LOOP (Lines 35-36):
    collision_target = tmp_path / "sample-compressed.pdf"
    shutil.copy(real_source, collision_target)

    # Run execution loop
    run(str(sandbox_input))

    # PHYSICAL VERIFICATIONS
    expected_incremented_file = tmp_path / "sample-compressed-1.pdf"
    assert expected_incremented_file.exists(), "The naming loop failed to create sample-compressed-1.pdf!"
    assert expected_incremented_file.stat().st_size > 0, "The output file size is empty!"


# ==============================================================================
# ALREADY-OPTIMIZED REDUCTION LOGGING TRACKING PASS
# ==============================================================================
def test_run_with_already_compressed_file_logs(tmp_path, capsys):
    """Verifies alternative console logging format if file sizing yields no changes."""
    test_root = Path(__file__).parent
    real_compressed_source = test_root / "data" / "compressed.pdf"

    if not real_compressed_source.exists():
        pytest.fail(f"Required testing asset missing at path: {real_compressed_source}")

    sandbox_input = tmp_path / "already_optimal.pdf"
    shutil.copy(real_compressed_source, sandbox_input)

    run(str(sandbox_input))
    captured = capsys.readouterr()

    assert "Output saved to" in captured.out
