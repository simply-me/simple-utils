"""Wrapper for interacting with PyMuPDF (fitz) via subprocess."""

import subprocess
from pathlib import Path


def run(action: str, pdf_path: str):
    """Run the specified action on the given PDF document using PyMuPDF CLI."""
    src = Path(pdf_path)
    if not src.exists():
        raise FileNotFoundError(f"Target PDF document absent at path: {src}")

    # Build the direct execution token chain using Python's module invoker
    cmd = ""
    if action == "info":
        cmd = ["python", "-m", "pymupdf", "info", str(src)]  # Native CLI call
    elif action == "clean":
        out_path = src.parent / f"{src.stem}_cleaned.pdf"
        cmd = [
            "python",
            "-m",
            "pymupdf",
            "clean",
            str(src),
            str(out_path),
        ]  # Native structural cleaner
        print(f"Output target generated for processing pipeline: {out_path}")

    print(f"Running Subprocess CLI: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False, text=True, check=False)

    if result.returncode != 0:
        raise RuntimeError(
            f"PyMuPDF CLI processing faulted with status code: {result.returncode}"
        )
