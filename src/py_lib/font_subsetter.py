"""Font subsetting utility leveraging fontTools via subprocess."""

import subprocess
import sys
from pathlib import Path


def run(
    font_path: str, chars: str = None, unicodes: str = None, explicit_out: Path = None
):
    """Run the font subsetting process using fontTools CLI with specified parameters."""
    src_font = Path(font_path)
    if not src_font.exists():
        raise FileNotFoundError(f"Target font binary file template absent: {src_font}")

    # Define standard production workspace destination routes if empty
    if not explicit_out:
        # Resolves automatically relative to runtime src paths
        explicit_out = (
            Path(__file__).parent.parent
            / "output"
            / f"{src_font.stem}_subset{src_font.suffix}"
        )

    explicit_out.parent.mkdir(parents=True, exist_ok=True)

    # 1. Map production arguments directly onto the pyftsubset / fontTools native syntax tree
    cmd = [
        "python",
        "-m",
        "fontTools.subset",
        str(src_font),
        f"--output-file={str(explicit_out)}",
        "--flavor=epub",  # Output uncompressed containers compatible with hardware reader panels
        "--layout-features='*'",  # Retain critical kerning and ligatures
        "--glyph-names",  # Keep system accessibility vectors readable
        "--no-hinting",  # Drop scale weight instructions to shrink sizing profiles
    ]

    # 2. Inject structural subset limits dynamically
    if chars:
        cmd.append(f"--text={chars}")
    elif unicodes:
        cmd.append(f"--unicodes={unicodes}")
    else:
        # Default safety block fallback limits
        cmd.append("--unicodes=U+0020-007E")

    print(f"Running Subprocess CLI: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)

    if result.returncode != 0:
        print(f"[❌ FontTools Failure Log]:\n{result.stderr}", file=sys.stderr)
        raise RuntimeError("Font subset compression engine aborted execution.")

    print(f"[✓] Complete! Optimized font file exported safely to:\n {explicit_out}")
