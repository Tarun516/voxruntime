# VoxRuntime

VoxRuntime is a learning-first implementation of a production voice-agent
runtime and reliability platform. Its initial domain is clinic appointment
management, while the runtime architecture remains domain-independent.

The project teaches both application design and the mechanics underneath it:
execution flow, asynchronous scheduling, data ownership, memory retention, CPU
use, network I/O, failure handling, and distributed correctness.

## Current Status

Phase 0 Checkpoints 0.1 and 0.2 are complete. The repository contains the
Python/domain skeleton, strong UUID identities, the canonical Appendix A event
registry, and a validated deterministic event envelope. Realtime media and
external providers have not been introduced yet.

The canonical design source is
`VoxRuntime_Production_Engineering_Design_v1.4.docx`. Sections 3-22 and
Appendices A-C contain canonical requirements; Sections 26 and 27 preserve
earlier review history.

## Engineering Priorities

1. Correctness before convenience.
2. Understanding before abstraction.
3. Measured behavior before optimization claims.
4. Explicit state, ownership, and failure semantics.
5. Small, executable checkpoints.
6. Deterministic tests before real provider integrations.

## Documentation Map

Start with the [learning path](docs/learning-path.md), then read the relevant
parts of the [first-principles handbook](docs/foundations.md). Use the glossary
for quick lookup and checkpoint notes for detailed code walkthroughs. Track
practice and open questions in the [learning journal](docs/learning-journal.md).

- [Learning method](docs/learning-method.md)
- [System overview](docs/architecture/system-overview.md)
- [Implementation roadmap](docs/implementation-roadmap.md)
- [Checkpoint 0.1 repository/domain skeleton](docs/checkpoints/00-01-repository-and-domain-skeleton.md)
- [Checkpoint 0.2 event model](docs/checkpoints/00-02-canonical-event-model.md)
- [Checkpoint template](docs/checkpoints/TEMPLATE.md)
- [Resource model](docs/resource-model.md)
- [Glossary](docs/glossary.md)
- [ADR template](docs/adr/TEMPLATE.md)

Repository-wide implementation rules are defined in [AGENTS.md](AGENTS.md).

## Planned First Milestone

Phase 0 freezes executable runtime contracts before any real media or provider
integration. It covers identifiers, events, state machines, causality,
cancellation, provider protocols, tool-operation semantics, and clock/latency
contracts.

Checkpoints 0.1 and 0.2 established package boundaries, test conventions,
strong identities, and the event contract. Checkpoint 0.3 will implement
orthogonal state machines; Phase 0 still does not run a live voice loop.

## Evidence Policy

Latency, concurrency, CPU, and memory figures begin as hypotheses. They become
accepted targets only after a reproducible benchmark records its environment,
workload, sample size, and measurement boundary.

## Checkpoint 0.1 Commands

Run these from the repository root:

```bash
uv sync --python 3.12
make check
UV_CACHE_DIR=.uv-cache uv run voxruntime
make inspect
make benchmark-events
```

`uv sync` creates `.venv`, resolves development dependencies, installs the
editable package, and updates `uv.lock`. `make check` runs four separate gates:
format consistency, lint rules, static type analysis, and behavioral tests.
The third command starts Python through the installed console entry point.
`make inspect` measures changes observed while importing the package.
`make benchmark-events` measures 10,000 local event JSON round trips with
allocation tracing; its result is diagnostic evidence rather than a capacity
target.

Generated identities vary on every run. Timing and memory observations also
vary with the machine and workload; compare recorded distributions rather than
expecting byte-for-byte identical measurement output.
