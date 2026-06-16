"""Registry and router for internal custom Python extensions."""

import argparse
from typing import List, Callable, Dict


def route_pdf_compress(forwarded_args: List[str]) -> None:
    """Extracts flags and directly runs the internal PDF optimization script."""
    # pylint: disable=import-outside-toplevel
    import pdf_optimizer

    # High-performance sub-parser to isolate exactly what pdf-compress needs
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--input", required=True, type=str, help="Path to source PDF.")

    # Safely digest known flags without crashing on unknown trailing parameters
    parsed_args, _ = parser.parse_known_args(forwarded_args)

    # Hand off execution to your single-argument engine function
    pdf_optimizer.run(pdf_path=parsed_args.input)


# Centralised type-hinted registry mapping target strings to execution functions
CUSTOM_INTERCEPTS: Dict[str, Callable[[List[str]], None]] = {
    "pdf-compress": route_pdf_compress,
}


def handle_custom_intercept(target: str, forwarded_args: List[str]) -> bool:
    """Checks if a target matches a custom tool script and routes execution."""
    if target in CUSTOM_INTERCEPTS:
        CUSTOM_INTERCEPTS[target](forwarded_args)
        return True
    return False
