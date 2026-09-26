"""Measure observable process changes caused by importing VoxRuntime."""

import importlib
import json
import resource
import sys
import threading
import time
import tracemalloc
from pathlib import Path

PROJECT_ROOT = Path(__file__).parents[1]
SOURCE_ROOT = PROJECT_ROOT / "src"


def resident_set_kib() -> int:
    """Return this process's peak resident-set size in kibibytes on Linux.

    Solution category:
        Operating-system resource observation through the standard library.

    Complexity:
        O(1) time and O(1) auxiliary space for one process-level query.

    Limitations:
        ``ru_maxrss`` is a peak, includes native/interpreter memory, and has
        platform-specific units. This project currently interprets Linux units.
    """
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss


def main() -> int:
    """Import VoxRuntime and emit a JSON snapshot of the measured changes.

    Returns:
        Process status ``0`` after writing one JSON object to standard output.

    Solution category:
        Before/after measurement using module-count and allocation snapshots.

    Complexity:
        O(a + m) time and space, where ``a`` is the number of traced allocation
        records and ``m`` is the number of loaded module names. Import work is
        determined by the package import graph. The tool performs no network I/O.
    """
    # 1. Make the source checkout importable without requiring prior installation.
    sys.path.insert(0, str(SOURCE_ROOT))

    # 2. Capture process and Python-allocation state immediately before import.
    tracemalloc.start()
    modules_before = frozenset(sys.modules)
    threads_before = threading.active_count()
    rss_before_kib = resident_set_kib()
    allocation_before = tracemalloc.take_snapshot()
    cpu_before = time.process_time_ns()
    wall_before = time.perf_counter_ns()

    # 3. Import through Python's normal import machinery.
    importlib.import_module("voxruntime")

    # 4. Capture the same signals after import and derive comparable differences.
    import_wall_ns = time.perf_counter_ns() - wall_before
    import_cpu_ns = time.process_time_ns() - cpu_before
    allocation_after = tracemalloc.take_snapshot()
    allocated_bytes = sum(
        statistic.size_diff
        for statistic in allocation_after.compare_to(allocation_before, "lineno")
    )
    imported_modules = sorted(set(sys.modules) - modules_before)

    report: dict[str, object] = {
        "python_version": sys.version.split()[0],
        "import_wall_ns": import_wall_ns,
        "import_cpu_ns": import_cpu_ns,
        "traced_allocation_change_bytes": allocated_bytes,
        "peak_rss_before_kib": rss_before_kib,
        "peak_rss_after_kib": resident_set_kib(),
        "thread_count_before": threads_before,
        "thread_count_after": threading.active_count(),
        "imported_module_count": len(imported_modules),
        "imported_modules": imported_modules,
    }

    # 5. Serialize the report for a human or later comparison tool.
    print(json.dumps(report, indent=2, sort_keys=True))
    tracemalloc.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
