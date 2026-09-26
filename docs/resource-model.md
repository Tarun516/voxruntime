# Runtime and Resource Model

## Purpose

This document evolves with the implementation. It connects source-level code
to processes, threads, async tasks, memory, CPU, file descriptors, sockets, and
durable storage.

Values marked **hypothesis** are expectations. Values marked **measured** must
include a reproducible environment and command.

## Current State

No runtime process exists yet. The repository is at documentation/planning
stage, so all execution topology below is proposed.

## Planned Process Topology

Initially, components remain modular packages and may share a process when
isolation is unnecessary.

| Process | Primary responsibility | Latency sensitivity |
|---|---|---|
| Control API | Configuration and administrative HTTP requests | Moderate |
| Session router | Admission, worker selection, authority setup | High at startup |
| Realtime worker | Concurrent live `SessionRuntime` instances | Critical |
| Tool service/worker | Business-operation execution and recovery | Operation-dependent |
| Evaluation worker | Offline simulated conversations | Throughput-oriented |

This does not require five network services at the start. Boundaries are
extracted only when scaling, failure isolation, security, or ownership
justifies the network hop.

## Realtime Worker Model

The intended initial model is one Python process with one primary asyncio event
loop and many session task groups.

```text
OS process
+-- main Python thread
    +-- asyncio event loop
        +-- worker heartbeat/readiness tasks
        +-- telemetry export tasks
        +-- SessionRuntime task group x active sessions
            +-- media receive
            +-- VAD/STT processing
            +-- turn management
            +-- reasoning/tool orchestration
            +-- TTS synthesis
            +-- media send
```

These are logical tasks, not automatically OS threads. A coroutine consumes
CPU while executing. An await can yield control when its operation is pending;
an already-ready awaitable may complete without suspension. Blocking code on
the event-loop thread delays unrelated sessions.

## Data Lifetime Classes

| Lifetime | Examples | Expected owner |
|---|---|---|
| Audio-frame | Normalized inbound/outbound frame | Bounded pipeline queue |
| Turn | Transcript, cancellation scope, generations | `SessionRuntime` |
| Session | Deployment artifact, conversation state | `SessionRuntime` |
| Worker | Provider pools, readiness, shared exporters | Worker process |
| Durable | Calls, epochs, operations, critical events | PostgreSQL/system of record |
| Artifact | Recordings, evaluation audio, exports | Object storage |

Every retained collection has a capacity, retention policy, or durable storage
strategy.

## CPU Model

Expected I/O-oriented work includes socket reads/writes, provider streams,
Redis, and PostgreSQL. Expected CPU-sensitive work includes audio conversion,
VAD, encoding/decoding, serialization, and any local inference.

CPU-heavy operations are benchmarked and, when necessary, moved to native
implementations, bounded executors, separate processes, or inference services.
Moving work off the event loop is not automatically an optimization: it adds
queueing, copying, context-switching, and cancellation complexity.

## Memory Model

The primary realtime memory risks are:

- unbounded audio or event queues;
- retaining complete audio unnecessarily;
- orphaned tasks holding session graphs alive;
- transcript/event histories cached without limits;
- repeated immutable-byte copies;
- provider SDK buffers outside visible application queues;
- telemetry buffering during exporter failure.

For each queue, record:

```text
capacity x average item size x number of sessions
```

Then add object/container overhead and provider/native buffers measured from a
representative process. Formulae are planning estimates until profiled.

## Measurement Record Template

```text
Date:
Commit/checkpoint:
Environment:
Python/runtime:
Command:
Workload:
Duration/sample size:
Wall time:
User/system CPU:
RSS baseline/peak/final:
Python allocated baseline/peak/final:
Task/thread/process count:
File descriptors/sockets:
Queue occupancy:
Event-loop lag:
Interpretation:
Limitations:
```

## Open Measurements

- Phase 0.1: interpreter and package-import baseline (recorded below).
- Phase 0: deterministic simulated-session task and allocation profile.
- Phase 1: per-session audio queue and provider-stream memory.
- Phase 2: interruption reaction and stale-buffer cleanup.
- Phase 6: safe sessions per worker under sustained load.

## Measurement Record: Checkpoint 0.1 Import Baseline

- Date: 2026-09-26
- Checkpoint: 0.1
- Environment: Linux x86_64 workspace container
- Runtime: CPython 3.12.13 in `.venv`
- Workloads: empty interpreter and `import voxruntime`
- Samples: five fresh processes for each `/usr/bin/time` workload
- Empty interpreter: 0.02 s wall; 11,156-11,376 KiB max RSS
- Package import: 0.06-0.07 s wall; 14,060-14,360 KiB max RSS
- Threads: one before and one after import in the diagnostic process
- Async tasks: none created by package import
- Network/file descriptors: not enumerated; source inspection and package
  contracts create no intentional network/file handles during import

One `tracemalloc` diagnostic run measured approximately 83.5 ms around import,
1,782,372 bytes of positive net traced allocation differences, and 20 newly
loaded modules. Tracing changes timing and memory behavior. The process had
already reached a peak RSS of 36,884 KiB before the measured import, so its
unchanged `ru_maxrss` cannot show that import allocated zero memory.

These results describe this environment and import graph. They are neither a
production budget nor a claim about a future realtime worker.

## Measurement Record: Checkpoint 0.2 Event Round Trips

- Date: 2026-09-26
- Runtime: CPython 3.12.13 in `.venv`
- Workload: 10,000 sequential serialize/deserialize cycles
- Representative wire size: 560 bytes
- Wall time: approximately 3.081 seconds
- Process CPU time: approximately 3.058 seconds
- Observed throughput: approximately 3,246 round trips/second
- Peak Python memory reported by `tracemalloc` during loop: 145,414 bytes
- Threads/tasks/network: one thread, no async tasks, no network I/O by design

The benchmark runs with allocation tracing, which changes cost. It retains only
the current serialized/restored event rather than a queue of 10,000 events.
Therefore the peak is evidence about this streaming loop, not memory required to
buffer 10,000 envelopes. Production capacity must be measured with real payload
distributions, queue bounds, concurrency, persistence, and telemetry.
