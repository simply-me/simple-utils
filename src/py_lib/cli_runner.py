"""Utility function to run any CLI tool with real-time streaming to console."""

import subprocess
import sys
from typing import Dict, List, Optional


def run(
    tool_args: List[str],
    mode: str = "py",
    working_dir: Optional[str] = None,
    custom_env: Optional[Dict[str, str]] = None,
) -> int:
    """Executes any CLI tool and leverages native OS-level stream piping.

    :param tool_args: A list of strings representing the tool and its flags/arguments.
    :param mode: Execution routing framework. Accepts 'py' or 'run'.
    :param working_dir: Path to the directory where the command should execute.
    :param custom_env: Optional dictionary to update environment variables.
    :return: The integer exit status code of the completed process.
    :raises ValueError: Raised on empty argument payloads or invalid structural modes.
    """
    if not tool_args:
        raise ValueError("The tool_args list cannot be empty.")

    if mode not in ["py", "run"]:
        raise ValueError(f"Unsupported routing engine profile: {mode}")

    # Normalise parameters to prevent double-nesting modules
    if mode == "py":
        if tool_args[0].lower() in ["python", "python3"]:
            tool_args = tool_args[1:]
        if tool_args and tool_args[0] == "-m":
            tool_args = tool_args[1:]
        full_command = [sys.executable, "-m"] + tool_args
    else:
        full_command = tool_args

    # Clean header with unified divider widths
    print(f"Running command: {' '.join(full_command)}\n{'-' * 50}")

    # Piping directly to sys.stdout lets the OS engine handle stream rendering at maximum speed.
    with subprocess.Popen(
        full_command,
        stdout=sys.stdout,
        stderr=sys.stderr,
        cwd=working_dir,
        env=custom_env,
    ) as process:
        returncode = process.wait()

    print("-" * 50)

    if returncode != 0:
        print(f"Process failed with exit code: {returncode}", file=sys.stderr)
    else:
        print("Process completed successfully.")

    return returncode
