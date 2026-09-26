"""Measure event serialization/deserialization on a repeatable local workload."""

import argparse
import json
import time
import tracemalloc
from datetime import UTC, datetime

from voxruntime.domain.identifiers import EventId, SessionId
from voxruntime.events.envelope import EventEnvelope
from voxruntime.events.types import DurabilityClass, EventType


def positive_int(raw: str) -> int:
    """Parse a command-line integer and require it to be positive.

    Solution category:
        Command-line boundary parsing and validation.

    Complexity:
        O(n) time for text length ``n`` and O(1) auxiliary space for bounded
        command-line input.
    """
    value = int(raw)
    if value < 1:
        raise argparse.ArgumentTypeError("value must be >= 1")
    return value


def parse_args() -> argparse.Namespace:
    """Parse the benchmark workload size from command-line arguments.

    Solution category:
        CLI configuration delegated to the standard-library argument parser.

    Complexity:
        O(a) time and space for ``a`` command-line arguments.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--iterations",
        type=positive_int,
        default=10_000,
        help="number of serialize/deserialize cycles (default: 10000)",
    )
    return parser.parse_args()


def benchmark(iterations: int) -> dict[str, int | float]:
    """Run deterministic event round trips and return measured process signals.

    Args:
        iterations: Number of complete serialization/deserialization cycles.

    Returns:
        Counts, elapsed/CPU nanoseconds, throughput, wire size, and peak traced
        Python allocation bytes.

    Solution category:
        Sequential microbenchmark with correctness checks inside the workload.

    Complexity:
        O(i * n) time for ``i`` iterations and serialized size ``n``. Retained
        auxiliary space is O(n); objects from previous iterations can be freed.

    Limitations:
        `tracemalloc` adds overhead, this is one process on one machine, and the
        payload is representative rather than a production distribution.
    """
    event = EventEnvelope(
        event_id=EventId.parse("22222222-2222-4222-8222-222222222222"),
        schema_version=1,
        event_type=EventType.STT_FINAL,
        durability_class=DurabilityClass.DIAGNOSTIC,
        session_id=SessionId.parse("11111111-1111-4111-8111-111111111111"),
        sequence_number=7,
        occurred_at=datetime(2026, 9, 26, 10, 30, tzinfo=UTC),
        clock_domain="benchmark-process",
        monotonic_offset_ns=1_000,
        payload={
            "transcript": "Please move my appointment to Wednesday afternoon.",
            "confidence": 0.98,
            "alternatives": ["Wednesday at 2 PM", "Wednesday at 4 PM"],
        },
    )
    expected_event_id = event.event_id

    # 1. Start measurements after constructing constant benchmark input.
    tracemalloc.start()
    cpu_started = time.process_time_ns()
    wall_started = time.perf_counter_ns()

    # 2. Exercise both directions and retain only the current iteration.
    serialized = ""
    for _ in range(iterations):
        serialized = event.to_json()
        restored = EventEnvelope.from_json(serialized)
        if restored.event_id != expected_event_id:
            raise AssertionError("event identity changed during round trip")

    # 3. Capture measurements before stopping allocation tracing.
    wall_ns = time.perf_counter_ns() - wall_started
    cpu_ns = time.process_time_ns() - cpu_started
    _, peak_traced_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        "iterations": iterations,
        "wire_bytes": len(serialized.encode("utf-8")),
        "wall_ns": wall_ns,
        "cpu_ns": cpu_ns,
        "round_trips_per_second": iterations / (wall_ns / 1_000_000_000),
        "peak_traced_bytes": peak_traced_bytes,
    }


def main() -> int:
    """Run the requested event benchmark and print one JSON report.

    Solution category:
        Command-line orchestration with no additional algorithm.

    Complexity:
        Dominated by ``benchmark``: O(i * n) time and O(n) retained space.
    """
    # 1. Convert CLI text into a validated workload configuration.
    arguments = parse_args()

    # 2. Run the measurement and serialize its small fixed result.
    report = benchmark(arguments.iterations)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
