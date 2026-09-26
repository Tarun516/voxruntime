# Implementation Roadmap

## Delivery Strategy

Use the [learning path](learning-path.md) for prerequisites and the
[teaching method](learning-method.md) for lesson delivery. The numbered list
below contains teaching slices, not replacements for canonical checkpoint IDs.
The learning path maps these slices to design checkpoints 0.1-0.8.

Implementation advances through runnable checkpoints. Later phases may be
replanned using evidence from earlier phases, but correctness invariants remain
stable unless the canonical design is deliberately revised.

## Phase 0: Runtime Contracts and Foundations

Goal: make the core vocabulary and correctness rules executable without real
media or provider dependencies.

Canonical progress: Checkpoints 0.1 (repository/domain skeleton) and 0.2
(canonical event model) are complete. Learner practice remains tracked
separately in the learning journal.

1. Repository and domain skeleton.
2. Core identifiers and immutable value objects.
3. Canonical event model and schema versioning.
4. Session lifecycle state machine.
5. Orthogonal turn/activity state machines.
6. Turn identity, generation identity, and stale-result rejection.
7. Structured cancellation.
8. Provider protocols and deterministic fakes.
9. Tool operation/attempt/recovery contract.
10. Clock domains and latency-span contract.
11. Integrated deterministic session simulation.
12. Phase 0 invariant and race-test suite.

Exit evidence:

- contracts are represented as typed code;
- invalid transitions and stale work are rejected in tests;
- deterministic fakes can drive an entire simulated turn;
- cancellation leaves no orphan tasks;
- tool ambiguity can end in `UNKNOWN` without duplicate dispatch;
- timing code never subtracts unrelated clock domains;
- the execution and resource model is documented.

## Phase 1: Minimal Browser Voice Runtime

Goal: establish one end-to-end browser voice loop with bounded queues and an
inspectable trace. Major checkpoints include `SessionRuntime`, LiveKit media,
streaming STT, LLM, TTS, playback, and the first runtime timeline.

## Phase 2: Realtime Conversation Semantics

Goal: implement local VAD, endpointing, overlapping synthesis/playback,
barge-in, delivery evidence, and deterministic realtime race tests.

## Phase 3: Safe Tool Runtime and Clinic Domain

Goal: introduce typed clinic tools, stable operation identities, idempotency,
`UNKNOWN`, reconciliation, compensation, and tool interruption semantics.

## Phase 4: Durable Control Plane and Recovery

Goal: add PostgreSQL schemas, immutable deployment artifacts, durable call and
tool records, session authority, atomic fencing, Class-A event handoff, named
reconcilers, and control-plane APIs.

## Phase 5: Telephony

Goal: support inbound SIP/PSTN, DTMF, PSTN delivery estimation, recording and
retention policies, and human transfer.

## Phase 6: Distributed Realtime Runtime

Goal: add worker registry, routing, leases, stale-owner fencing, media
publication authority, admission control, drain behavior, partition policy,
and measured capacity.

## Phase 7: Production Observability

Goal: deliver OpenTelemetry instrumentation, operational metrics, call
timelines, causal latency waterfalls, cost attribution, and failure
classification.

## Phase 8: Evaluation and Agent CI/CD

Goal: implement versioned scenarios, deterministic assertions, text and voice
simulation, realtime metrics, constrained model-assisted judges, comparisons,
and regression gates.

## Phase 9: Production Hardening

Goal: validate timeout/retry policies, circuit breakers, bulkheads, quotas,
security controls, chaos behavior, sustained load, leaks, and runbooks.

## Phase 10: Self-Hosted Inference

Goal: explore self-hosted STT/TTS/LLM serving only after the provider-backed
runtime is correct and measurable. GPU scheduling, batching, caching,
quantization, and routing decisions require benchmark evidence.

## Scope Rule

Only the active checkpoint is implementation scope. It may define extension
points required by the design, but it must not pre-build future phases.
