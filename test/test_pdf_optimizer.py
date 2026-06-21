import shutil
import sys
from pathlib import Path

import pytest
from pdf_optimizer import _run_isolated_worker, print_progress, run


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

    # FORCE NAMING COLLISION LOOP
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


# ==============================================================================
# DIRECT WORKER METHOD COVERAGE
# ==============================================================================
def test_isolated_worker_direct_execution(tmp_path):
    """Directly invokes the background worker method to cover internal layout cleaning lines."""
    test_root = Path(__file__).parent
    real_source = test_root / "data" / "uncompressed.pdf"

    if not real_source.exists():
        pytest.fail(f"Required testing asset missing at path: {real_source}")

    sandbox_input = tmp_path / "worker_input.pdf"
    sandbox_output = tmp_path / "worker_output.pdf"
    shutil.copy(real_source, sandbox_input)

    # Invoke the worker method directly in-process to allow pytest-cov to trace it
    _run_isolated_worker(str(sandbox_input), str(sandbox_output))

    assert sandbox_output.exists()
    assert sandbox_output.stat().st_size > 0


# ==============================================================================
# SEGFAULT ERROR EXCEPTION COVERAGE
# ==============================================================================
def test_run_handles_segmentation_fault_exception(tmp_path, monkeypatch):
    """Mocks a bad subprocess return code to hit the emergency fallback RuntimeError branch."""
    sandbox_input = tmp_path / "crash_sample.pdf"
    sandbox_input.write_text("dummy content")

    class MockCompletedProcess:
        returncode = -11  # Simulates standard Access Violation exit code
        stdout = "Finalizing layout...\n"
        stderr = "Segmentation fault core dumped\n"

    # FIXED: Target the specific imported module namespace for the patch to stick
    import pdf_optimizer

    monkeypatch.setattr(pdf_optimizer.subprocess, "run", lambda *args, **kwargs: MockCompletedProcess())

    with pytest.raises(RuntimeError) as exc_info:
        run(str(sandbox_input))

    assert "C-layer segmentation fault" in str(exc_info.value)


# ==============================================================================
# CLI ENTRY HOOK INITIALIZATION COVERAGE
# ==============================================================================
def test_cli_worker_mode_routing(tmp_path, monkeypatch):
    """Mocks sys.argv to fully cover the entry checkpoint conditions in run()."""
    import pdf_optimizer

    sandbox_input = tmp_path / "cli_src.pdf"
    sandbox_dest = tmp_path / "cli_dest.pdf"
    sandbox_input.write_text("dummy source payload")

    # FIXED: Align list elements to exactly match EXPECTED_WORKER_ARGS_COUNT (4 elements)
    # This triggers the 'if len(sys.argv) == 4:' branch inside pdf_optimizer.run()
    mock_args = ["pdf_optimizer.py", "--subprocess-worker-mode", str(sandbox_input), str(sandbox_dest)]
    monkeypatch.setattr(sys, "argv", mock_args)

    worker_called = False

    def mock_worker(src_str, dest_str):
        nonlocal worker_called
        worker_called = True

    # Override the worker execution block path to check routing
    monkeypatch.setattr(pdf_optimizer, "_run_isolated_worker", mock_worker)

    pdf_optimizer.run(str(sandbox_input))
    assert worker_called is True
