import os


def test_verify_imports_are_sandboxed() -> None:
    """Verifies that tests hit build/src/py_lib during pipelines (build.sh/GitHub Actions),

    and src/py_lib during local development.
    """
    # 1. Look for pipeline environments using the system variable directly
    is_sandboxed_run = "build" in os.environ.get("PYTHONPATH", "")

    # 2. Native import (relies entirely on your build.sh or GitHub Action env paths)
    import main

    # 3. Resolve the absolute path of the loaded main module
    loaded_from = os.path.abspath(main.__file__).replace("\\", "/")

    # 4. Run the assertions to confirm isolation
    if is_sandboxed_run:
        assert "build/src/py_lib" in loaded_from, (
            f"CRITICAL PIPELINE ERROR: Tests are hitting original source files instead of the sandbox! "
            f"Loaded from: {loaded_from}"
        )
        print("-> SUCCESS: Verified testing against the build environment.")
    else:
        assert "src/py_lib" in loaded_from and "build" not in loaded_from, (
            f"CRITICAL DEV ERROR: Tests are not hitting the local source root! Loaded from: {loaded_from}"
        )
        print("-> SUCCESS: Verified testing against the local development source root.")
