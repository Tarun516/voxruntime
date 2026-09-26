"""Process-level tests for importing and executing the installed package."""

import os
import subprocess
import sys
from pathlib import Path
from uuid import UUID

PROJECT_ROOT = Path(__file__).parents[2]


def python_environment() -> dict[str, str]:
    """Create a minimal environment that exposes this source checkout.

    Solution category:
        Test-environment construction; no special algorithm applies.

    Complexity:
        O(e) time and space, where ``e`` is the number of inherited environment
        entries copied before adding the source path.
    """
    # 1. Copy so the test never mutates the parent process environment.
    environment = os.environ.copy()

    # 2. Point child imports at src/ while preserving normal process isolation.
    environment["PYTHONPATH"] = str(PROJECT_ROOT / "src")
    return environment


def test_package_import_has_no_output_or_extra_threads() -> None:
    """Importing VoxRuntime stays quiet and starts no background threads."""
    program = (
        "import threading; before=threading.active_count(); "
        "import voxruntime; after=threading.active_count(); "
        "raise SystemExit(0 if before == after == 1 else 1)"
    )

    result = subprocess.run(
        [sys.executable, "-c", program],
        cwd=PROJECT_ROOT,
        env=python_environment(),
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == ""
    assert result.stderr == ""


def test_module_entrypoint_prints_one_session_and_succeeds() -> None:
    """The operating-system process can reach and use the domain package."""
    result = subprocess.run(
        [sys.executable, "-m", "voxruntime"],
        cwd=PROJECT_ROOT,
        env=python_environment(),
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    prefix = "VoxRuntime session: "
    assert result.stdout.startswith(prefix)
    UUID(result.stdout.removeprefix(prefix).strip())
