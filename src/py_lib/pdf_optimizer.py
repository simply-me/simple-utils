"""Optimize and compress PDF files to reduce size.

This module provides wrappers around optimization engines
to compress streams, fonts, and images.
"""

import sys
from pathlib import Path
import fitz


def print_progress(current: int, total: int, prefix: str = "Processing"):
    """Generates a native, clean text-based progress bar in the terminal."""
    percent = (current / total) * 100
    bar_length = 30
    filled_length = int(bar_length * current // total)
    progress_bar = "#" * filled_length + "-" * (bar_length - filled_length)

    sys.stdout.write(
        f"\r{prefix}: |{progress_bar}| {percent:.1f}% ({current}/{total} pages)"
    )
    sys.stdout.flush()


# FIXED: Removed output_path parameter to enforce deterministic naming rules
def run(pdf_path: str):
    """Run the PDF optimization process on the specified input file."""
    src = Path(pdf_path)
    if not src.exists():
        raise FileNotFoundError(f"Target document absent: {src}")

    # FIXED: Always maps output path to parent directory with a '-compressed' suffix modifier
    dest = src.with_name(f"{src.stem}-compressed{src.suffix}")

    print(f"Initiating optimization pass on: {src.name}")
    doc = fitz.open(src)
    total_pages = len(doc)

    # 1. High-Efficiency Image Compression Pass
    print("Analyzing embedded images (skipping assets under 150 DPI)...")
    doc.rewrite_images(dpi_threshold=150, dpi_target=72, quality=50)

    # 2. Page Stream Optimization with Real-Time Progress Visuals
    print("Optimizing structural page streams...")
    for index, page in enumerate(doc, start=1):
        page.clean_contents()
        print_progress(index, total_pages, prefix="Compressing")

    print("\nFinalizing binary serialization and compression layers...")

    # 3. Structural Document Save
    doc.save(
        dest,
        garbage=4,
        deflate=True,
        clean=True,
        linear=True,
        use_objstms=True,
    )
    doc.close()

    orig_mbs = src.stat().st_size / (1024 * 1024)
    new_mbs = dest.stat().st_size / (1024 * 1024)

    print(
        f"{'-' * 50}\n"
        f"Compression completed successfully.\n"
        f"File size reduced from {orig_mbs:.2f} MB to {new_mbs:.2f} MB."
    )
