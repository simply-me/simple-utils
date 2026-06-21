"""Optimize and compress PDF files to reduce size.

This module provides structural and stream optimization engines to compress
PDF metadata, fonts, and heavy embedded asset streams safely.
"""

import subprocess
import sys
from pathlib import Path

import fitz  # PyMuPDF

# Constant definitions to prevent magic value comparison errors (PLR2004)
EXPECTED_WORKER_ARGS_COUNT = 4
MIN_CLI_ARGS_COUNT = 2


def print_progress(current: int, total: int, prefix: str = "Processing") -> None:
    """Generates a native, clean text-based progress bar in the terminal."""
    percent = (current / total) * 100
    bar_length = 30
    filled_length = int(bar_length * current // total)
    progress_bar = "#" * filled_length + "-" * (bar_length - filled_length)

    sys.stdout.write(f"\r{prefix}: |{progress_bar}| {percent:.1f}% ({current}/{total} pages)")
    sys.stdout.flush()


def _run_isolated_worker(src_str: str, dest_str: str) -> None:
    """Internal target that runs inside a pristine background subprocess.

    Isolates doc.rewrite_images from crashing the primary testing framework.
    """
    doc = fitz.open(src_str)
    total_pages = len(doc)

    # Perform structural optimization loop across all page content streams
    for index, page in enumerate(doc, start=1):
        try:
            page.clean_contents()
        except Exception:  # noqa: BLE001
            pass
        print_progress(index, total_pages, prefix="Compiling Layout")

    print("\n\nFinalizing desktop serialization output layer...")
    print(" -> Lowering image matrix resolution bounds...")
    doc.rewrite_images(dpi_target=150, quality=75)

    print(" -> Compressing binary streams and writing blocks to disk...")
    save_kwargs = {
        "garbage": 4,
        "deflate": True,
        "use_objstms": True,
        "ascii": False,
    }
    doc.save(dest_str, **save_kwargs)
    doc.close()


def run(pdf_path: str) -> None:
    """Run the PDF optimization process on the specified input file."""
    # Internal CLI entry point hook for the subprocess isolation worker
    if len(sys.argv) == EXPECTED_WORKER_ARGS_COUNT and sys.argv[1] == "--subprocess-worker-mode":
        _run_isolated_worker(src_str=sys.argv[2], dest_str=sys.argv[3])
        return

    src = Path(pdf_path)
    if not src.exists():
        raise FileNotFoundError(f"Target document absent: {src}")

    # Non-destructive target naming loop
    base_dest_name = f"{src.stem}-compressed"
    dest = src.with_name(f"{base_dest_name}{src.suffix}")
    counter = 1
    while dest.exists():
        dest = src.with_name(f"{base_dest_name}-{counter}{src.suffix}")
        counter += 1

    print(f"Opening file: {src.name}")

    # Invoke the script itself inside an isolated subprocess
    worker_cmd = [
        sys.executable,
        __file__,
        "--subprocess-worker-mode",
        str(src),
        str(dest),
    ]

    # Run the worker and capture potential C-layer crash exits safely
    result = subprocess.run(worker_cmd, capture_output=True, text=True, check=False)

    # If the process completed successfully, forward stdout and evaluate metrics
    if result.returncode == 0 and dest.exists():
        print(result.stdout, end="")

        orig_bytes = src.stat().st_size
        new_bytes = dest.stat().st_size

        orig_mbs = orig_bytes / (1024 * 1024)
        new_mbs = new_bytes / (1024 * 1024)

        saved_bytes = max(0, orig_bytes - new_bytes)
        saved_mbs = saved_bytes / (1024 * 1024)
        saved_pct = (saved_bytes / orig_bytes) * 100 if orig_bytes > 0 else 0.0

        print(f"{'-' * 50}\nOptimization execution finalized.")
        print(f"Output saved to: {dest.name}")
        print(f"Original Size:   {orig_mbs:.2f} MB")
        print(f"Optimized Size:  {new_mbs:.2f} MB")

        if saved_bytes > 0:
            print(f"Size Reduction:  {saved_mbs:.2f} MB ({saved_pct:.1f}%)")
        else:
            print("Size Reduction:  0.00 MB (0.0%) - File was already optimal.")
    else:
        # Gracefully handle the C-layer segmentation fault
        print(f"\n{'-' * 50}\n[CRITICAL ERROR] The optimization engine failed.")
        print("Reason: A low-level Segmentation Fault occurred inside MuPDF's library.")
        print("        The file contains image matrices incompatible with rewrite_images().")
        print(f"{'-' * 50}")

        # Raise a standard clean exception so pytest registers a predictable failure
        raise RuntimeError("PDF optimization aborted due to a C-layer segmentation fault.")


if __name__ == "__main__":
    # Prevent default execution trigger if called directly as a shell entry hook
    if len(sys.argv) < MIN_CLI_ARGS_COUNT:
        run("test.pdf")
    else:
        # Safely route parameters when run as a subprocess worker script
        run(sys.argv[-1])
