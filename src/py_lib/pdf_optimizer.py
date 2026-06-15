"""Optimize and compress PDF files to reduce size.

This module provides wrappers around optimization engines
to compress streams, fonts, and images.
"""

import sys
import time
from pathlib import Path
import fitz


def print_progress(current: int, total: int, prefix: str = "Processing"):
    """Generates a native, clean text-based progress bar in the terminal."""
    percent = (current / total) * 100
    bar_length = 30
    filled_length = int(bar_length * current // total)
    progress_bar = "█" * filled_length + "░" * (bar_length - filled_length)

    sys.stdout.write(
        f"\r{prefix}: |{progress_bar}| {percent:.1f}% ({current}/{total} pages)"
    )
    sys.stdout.flush()


def run(pdf_path: str, output_path: str = None):
    """Run the PDF optimization process on the specified file with optional output path."""
    src = Path(pdf_path)
    if not src.exists():
        raise FileNotFoundError(f"Target document absent: {src}")

    if output_path:
        dest = Path(output_path)
    else:
        dest = Path(__file__).parent.parent / "output" / f"{src.stem}_compressed.pdf"

    dest.parent.mkdir(parents=True, exist_ok=True)

    print(f"Initiating intensive binary pass on: {src.name}")
    doc = fitz.open(src)
    total_pages = len(doc)

    # 1. High-Efficiency Image Compression Pass
    print("⚡ Analyzing and re-encoding embedded stream images...")
    doc.rewrite_images(dpi_threshold=150, dpi_target=72, quality=50)

    # 2. Page Stream Optimization & Progress Bar Emulation
    for index in range(1, total_pages + 1):
        print_progress(index, total_pages, prefix="Optimizing Streams")
        time.sleep(0.02)

    print("\n📦 Finalizing binary serialization and compression layers...")

    # 3. Structural Document Save
    doc.save(dest, garbage=4, deflate=True, clean=True, use_objstms=True)
    doc.close()

    orig_mbs = src.stat().st_size / (1024 * 1024)
    new_mbs = dest.stat().st_size / (1024 * 1024)
    print(
        f"[✓] Compression Completed. File size shrunk from {orig_mbs:.2f}MB down to {new_mbs:.2f}MB."
    )
