"""Optimize and compress PDF files to reduce size.

This module provides structural and stream optimization engines to compress
PDF metadata, fonts, and heavy embedded asset streams safely.
"""

import sys
from pathlib import Path

import fitz  # PyMuPDF


def print_progress(current: int, total: int, prefix: str = "Processing") -> None:
    """Generates a native, clean text-based progress bar in the terminal."""
    percent = (current / total) * 100
    bar_length = 30
    filled_length = int(bar_length * current // total)
    progress_bar = "#" * filled_length + "-" * (bar_length - filled_length)

    sys.stdout.write(f"\r{prefix}: |{progress_bar}| {percent:.1f}% ({current}/{total} pages)")
    sys.stdout.flush()


def run(pdf_path: str) -> None:
    """Run the PDF optimization process on the specified input file."""
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
    doc = fitz.open(src)
    total_pages = len(doc)

    # Perform structural optimization loop across all page content streams
    for index, page in enumerate(doc, start=1):
        try:
            page.clean_contents()
        except Exception:  # pragma: no cover
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
    doc.save(dest, **save_kwargs)
    doc.close()

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


if __name__ == "__main__":
    run("test.pdf")
