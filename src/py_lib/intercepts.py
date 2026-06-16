"""Registry and router for internal custom Python extensions."""

import argparse
from typing import Callable, Dict, List


def route_pdf_compress(forwarded_args: List[str]) -> None:
    """Extracts the positional path argument and runs the PDF optimization script.

    :param forwarded_args: Raw arguments forwarded down from the main CLI router.
    """
    # pylint: disable=import-outside-toplevel
    import pdf_optimizer

    # High-performance sub-parser accepting a single positional file argument
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("pdf_path", type=str, help="Path to the source PDF file.")

    parsed_args, _ = parser.parse_known_args(forwarded_args)

    pdf_optimizer.run(pdf_path=parsed_args.pdf_path)


# Centralised type-hinted registry mapping target strings to execution functions
CUSTOM_INTERCEPTS: Dict[str, Callable[[List[str]], None]] = {
    "pdf-compress": route_pdf_compress,
}


def handle_custom_intercept(target: str, forwarded_args: List[str]) -> bool:
    """Checks if a target matches a custom tool script and routes execution.

    :param target: Target application or tool name keyword.
    :param forwarded_args: Downstream trailing parameters to process.
    :return: True if intercepted and handled locally, False otherwise.
    """
    if target in CUSTOM_INTERCEPTS:
        CUSTOM_INTERCEPTS[target](forwarded_args)
        return True
    return False
