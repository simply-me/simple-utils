"""Utility function to run any CLI tool with real-time streaming to console."""

import subprocess
import sys
from typing import List, Optional, Dict


def run(
    tool_args: List[str],
    is_python_module: bool = True,
    working_dir: Optional[str] = None,
    custom_env: Optional[Dict[str, str]] = None,
) -> int:
    """Executes any CLI tool and streams its stdout/stderr in real time to the console.

    :param tool_args: A list of strings representing the tool and its flags/arguments.
    :param is_python_module: If True, prepends sys.executable + "-m" to isolate the call.
    :param working_dir: Path to the directory where the command should execute.
    :param custom_env: Optional dictionary to update environment variables.
    :return: The integer exit status code of the completed process.
    """
    if not tool_args:
        raise ValueError("The tool_args list cannot be empty.")

    # Normalise parameters to prevent double-nesting modules
    if is_python_module:
        if tool_args[0].lower() in ["python", "python3"]:
            tool_args = tool_args[1:]
        if tool_args[0] == "-m":
            tool_args = tool_args[1:]
        full_command = [sys.executable, "-m"] + tool_args
    else:
        full_command = tool_args

    print(f"[Launcher] Running: {' '.join(full_command)}\n" + "-" * 60)

    try:
        # Open the process with piped streams and real-time line buffering
        # Read the stream buffer line-by-line while the process runs
        # Open the process with piped streams and real-time line buffering
        with subprocess.Popen(
            full_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Merges stderr into stdout stream for sequential printing
            text=True,  # Decodes raw bytes to readable string text automatically
            bufsize=1,  # Line buffered tracking
            cwd=working_dir,
            env=custom_env,
        ) as process:

            # Read the stream buffer line-by-line while the process runs
            while True:
                line = process.stdout.readline() if process.stdout else ""
                if not line and process.poll() is not None:
                    break
                if line:
                    sys.stdout.write(line)
                    sys.stdout.flush()

            # Wait for the official shutdown tracking loop to finish up
            returncode = process.wait()

        print("-" * 60)

        if returncode != 0:
            print(f"[CRITICAL] Process failed with exit code: {returncode}")
            raise subprocess.CalledProcessError(returncode, full_command)

        print("[SUCCESS] Process completed without errors.")
        return returncode

    except Exception as e:
        print(f"[ERROR] Subprocess system routing failed: {e}")
        raise


if __name__ == "__main__":
    print("--- Executing Standalone Diagnostic Test ---")

    # FIX: Pass an actual module name ('pip') along with its flag ('--version')
    print("\n[Test 1] Running Python module version test...")
    test_args_1 = ["pip", "--version"]
    exit_code_1 = run(tool_args=test_args_1, is_python_module=True)
    print(f"Test 1 exited with code: {exit_code_1}")

    # Test 2: Native system command test
    print("\n[Test 2] Running native system continuous output test...")
    import platform

    ping_flag = "-n" if platform.system() == "Windows" else "-c"

    test_args_2 = ["ping", ping_flag, "3", "127.0.0.1"]
    exit_code_2 = run(tool_args=test_args_2, is_python_module=False)
    print(f"Test 2 exited with code: {exit_code_2}")
