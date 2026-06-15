"""Python CLI Application Launcher and Subprocess Router."""

import sys
import argparse
from typing import List

# Imports our real-time streaming runner function from cli_runner.py
import cli_runner


def parse_application_args() -> argparse.Namespace:
    """Sets up the argument parser to extract the target tool and configuration flags."""
    parser = argparse.ArgumentParser(
        description="Generic Python Launcher and Subprocess CLI Router.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py pymupdf clean input.pdf output.pdf
  python main.py git status --exe
        """,
    )

    # The tool to execute (e.g., 'pymupdf', 'pylint', 'git')
    parser.add_argument(
        "tool",
        type=str,
        help="The name of the CLI tool or Python module you want to run.",
    )

    # Captures all subsequent flags, options, and file paths passed behind the tool
    parser.add_argument(
        "args",
        nargs=argparse.REMAINDER,
        help="All additional positional and optional arguments to forward to the tool.",
    )

    # An optional switch if you want to explicitly declare it's a standalone native binary
    parser.add_argument(
        "--exe",
        action="store_true",
        help="Forces execution of exe instead of a local .venv Python module.",
    )

    return parser.parse_args()


def main() -> None:
    """Main entry point for the CLI application launcher."""
    # 1. Protection Check: Ensure at least one argument was passed down to the interpreter
    if len(sys.argv) < 2:
        print("[ERROR] Minimal parameters missing.")
        print("Usage: python main.py <tool_name> [tool_arguments...] [--exe]")
        sys.exit(1)

    # 2. Extract and parse parameters
    parsed_args = parse_application_args()

    # 3. Combine the primary tool name and trailing arguments into a single execution list
    full_tool_command: List[str] = [parsed_args.tool] + parsed_args.args

    # If the user passed '--exe' explicitly, we tell the runner not to append 'python -m'
    is_module = not parsed_args.exe

    print("[Application Execution Router Initialised]")

    try:
        # 4. Forward the constructed command array to the real-time stream monitor
        exit_code = cli_runner.run(
            tool_args=full_tool_command, is_python_module=is_module
        )
        sys.exit(exit_code)

    except Exception as e:
        # Gracefully exit if a critical execution or pipeline breakage happened
        print(f"[CRITICAL] Router crashed due to system error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
