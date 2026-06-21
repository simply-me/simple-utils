"""Simple Python CLI Application Launcher and Subprocess Router."""

import argparse
import pathlib
import shlex
import sys
from typing import List

import cli_runner
import intercepts


def get_version() -> str:
    """Reads the static raw version number text file managed by Commitizen."""
    try:
        # Resolves the path to '.version' sitting right next to this main.py file
        version_file_path = pathlib.Path(__file__).parent / ".version"

        # Read the single-line string and strip trailing whitespace/newlines
        return version_file_path.read_text(encoding="utf-8").strip()
    except Exception:  # noqa: BLE001
        return "no-version"


def parse_launcher_mode(parser_args: List[str]) -> argparse.Namespace:
    """Parses only the initial routing command, leaving downstream flags untouched."""
    parser = argparse.ArgumentParser(
        description="Simply: A minimal CLI launcher and subprocess router.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("mode", choices=["run", "py"])
    parser.add_argument("target", type=str)

    parsed, remaining_args = parser.parse_known_args(parser_args)
    parsed.downstream_args = remaining_args
    return parsed


def main() -> None:
    """Main entry point for the simplified application launcher."""
    raw_args = sys.argv[1:]

    # Unpack the single packed macro string passed by the Windows CMD wrapper
    if len(raw_args) == 1:
        forwarded_tokens = shlex.split(raw_args[0])
    else:
        forwarded_tokens = raw_args

    if not forwarded_tokens:
        print("[ERROR] No execution parameters reached the core engine.", file=sys.stderr)
        sys.exit(2)

    parsed_config = parse_launcher_mode(forwarded_tokens)
    forwarded_args = parsed_config.downstream_args

    # Reads the version and prints it
    version = get_version()
    print(f"Simply Launcher v{version}")
    print(f"Routing execution via mode: '{parsed_config.mode}'")
    print(f"{'-' * 50}\n")

    try:
        # Run custom intercepts first
        if parsed_config.mode == "py" and intercepts.handle_custom_intercept(
            target=parsed_config.target, forwarded_args=forwarded_args
        ):
            exit_code = 0
        else:
            full_tool_command: List[str] = [parsed_config.target] + forwarded_args
            exit_code = cli_runner.run(tool_args=full_tool_command, mode=parsed_config.mode)

        print()
        # Cleanly bubble the exact downstream tool code without extra router text
        sys.exit(exit_code)

    except Exception as e:  # noqa: BLE001
        # Keep this only for unexpected crashes in python itself (e.g. system files missing)
        print(f"\n{'=' * 50}\nCRITICAL ROUTER ERROR: {e}\n{'=' * 50}\n", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
