"""Simplified Python CLI Application Launcher and Subprocess Router."""

import sys
import argparse
from typing import List
import cli_runner


def parse_launcher_mode(parser_args: List[str]) -> argparse.Namespace:
    """Parses only the initial routing command, leaving downstream flags untouched."""
    parser = argparse.ArgumentParser(
        description="Simplified CLI Subprocess Router.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
   simply run git status
   simply run pyftsubset --input font.ttf --output font-subset.ttf --unicodes=U+0020-007E
   simply py pymupdf --input document.pdf --output compressed.pdf
   simply py pdf_optimizer --input document.pdf --output compressed.pdf
   """,
    )

    parser.add_argument(
        "mode",
        choices=["run", "py"],
        help="Execution mode: 'run' for system binaries, 'py' for python modules.",
    )

    parser.add_argument(
        "target",
        type=str,
        help="The name of the executable or Python module.",
    )

    parsed, remaining_args = parser.parse_known_args(parser_args)
    parsed.downstream_args = remaining_args
    return parsed


def main() -> None:
    """Main entry point for the simplified application launcher."""
    raw_args = sys.argv[1:]

    parsed_config = parse_launcher_mode(raw_args)

    forwarded_args = parsed_config.downstream_args
    if forwarded_args and forwarded_args == "--":
        forwarded_args = forwarded_args[1:]

    full_tool_command: List[str] = [parsed_config.target] + forwarded_args

    print(f"[Router Initialised | Mode: {parsed_config.mode}]")

    try:
        exit_code = cli_runner.run(tool_args=full_tool_command, mode=parsed_config.mode)
        sys.exit(exit_code)

    except Exception as e:
        print(f"[CRITICAL] Router crashed due to execution error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
