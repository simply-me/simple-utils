"""Pipeline workflow module.

Orchestrates the end-to-end process of extracting character usage
from an ePub and subsetting a font accordingly.
"""

from pathlib import Path
import fitz
import font_subsetter


def run(epub_path: str, font_path: str):
    """Run the multi-pass pipeline workflow to subset a font based on ePub character usage."""
    book_src = Path(epub_path)
    font_src = Path(font_path)

    if not book_src.exists():
        raise FileNotFoundError(f"Book file path invalid: {book_src}")
    if not font_src.exists():
        raise FileNotFoundError(f"Target system font template invalid: {font_src}")

    print(f"Extracting character blueprint map from ePub layout: {book_src.name}...")

    # 1. Fast in-memory array iteration scan via PyMuPDF
    doc = fitz.open(book_src)
    tracked_characters = set()

    for page in doc:
        # Scrape and add raw string contents to the filter set automatically
        tracked_characters.update(page.get_text())
    doc.close()

    # Clean character listings of layout codes or carriage line brakes
    filtered_string = "".join(
        [char for char in tracked_characters if char not in ("\n", "\r", "\t")]
    )
    print(
        f" Map complete. Discovered {len(filtered_string)} discrete individual characters used."
    )

    # 2. Build our explicit export target path
    output_font = (
        book_src.parent.parent
        / "output"
        / f"{font_src.stem}_book_subset{font_src.suffix}"
    )

    # 3. Pipe directly into your fontTools CLI subprocess engine module block
    print("Forwarding structural character filters to the Subprocess CLI module...")
    font_subsetter.run(
        font_path=str(font_src), chars=filtered_string, explicit_out=output_font
    )
