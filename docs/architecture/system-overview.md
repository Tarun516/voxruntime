# System Overview

## Objective

VoxRuntime runs responsive voice conversations while preserving correctness
when callers interrupt, providers slow down, tools fail, workers restart, or
coordination infrastructure becomes temporarily unavailable.

The first product scenario is a clinic appointment agent. The core runtime is
domain-independent.

## Architectural Planes

```text
                         CONTROL PLANE

  Dashboard/API -> agent versions -> immutable deployment artifact
       |                 |                       |
       +-> analytics     +-> tool/policy refs    +-> session startup

  -----------------------------------------------------------------------

                       REALTIME DATA PLANE

  Browser/WebRTC --+
                   +--> media transport --> session router --> worker
  PSTN/SIP --------+                                      |
                                                          v
      inbound audio -> VAD -> STT -> turn manager -> agent runtime
                                                       |        |
                                                   tools/LLM    v
                                                       |     streaming TTS
                                                       +-------> playback

  -----------------------------------------------------------------------

                  DURABILITY AND OBSERVABILITY

  PostgreSQL: durable authority, configuration, operations, call truth
  Redis: ephemeral leases, readiness, routing, and rate-limit state
  Object store: recordings and large artifacts
  Telemetry: events, metrics, logs, and causal traces
```

## Control Plane

The control plane defines behavior. It owns tenants, agents, immutable
versions, deployment mappings, tool definitions, provider credential
references, evaluation suites, and administrative APIs.

An active call must not query the control plane on every audio frame or token.
At session startup, the worker receives or resolves the immutable deployment
artifact required for that call. The call remains pinned to it.

## Realtime Data Plane

A realtime worker hosts multiple independent `SessionRuntime` instances. Each
session coordinates bounded pipelines for media ingress, VAD, STT, endpointing,
agent reasoning, tool operations, TTS, playback, cancellation, and telemetry.

The model is concurrent rather than a single linear turn state. The caller may
start speaking while model generation, speech synthesis, or playback is still
active. Input, reasoning, synthesis, playback, and tool execution therefore
have orthogonal state.

## Core Identity Domains

Different identities solve different stale-work problems:

- `session_id`: identifies the call/runtime.
- `ownership_epoch`: identifies the current distributed owner.
- `turn_id` and `turn_epoch`: identify conversational input and supersession.
- `output_generation`: identifies synthesized/playable response output.
- `publication_generation`: identifies authority to publish media.
- `operation_id`: identifies one logical tool side effect across attempts.
- `event_id`: identifies one canonical event for idempotent consumption.

These values are not interchangeable. Carrying an identity is also not enough;
the authoritative boundary validates it before accepting a mutation.

## Session Ownership

Durable storage is the source of monotonic ownership epochs. Redis leases help
detect liveness and route work but cannot invent or reset authority.

Activation order is:

1. Select an eligible ready worker.
2. Transactionally issue and persist a new ownership epoch.
3. Associate the ephemeral lease with that epoch.
4. Admit worker activation and media publication.

If durable epoch issuance is unavailable, no new owner is created. Protected
writes validate the supplied epoch against current authority atomically with
the mutation.

## Tool Side Effects

A logical tool operation is distinct from a network attempt. Before sending a
side-effecting request, VoxRuntime durably records recoverable intent and the
attempt. A lost response does not prove failure: the operation becomes
`UNKNOWN` and is reconciled using the same logical identity.

Ownership transfer after dispatch does not permit repeating the business
action as a new operation.

## Conversation Truth

Generated text is not identical to speech delivered to a caller. Output is
split into identified segments that relate source text to synthesized audio and
delivery evidence.

Possible evidence includes client playback acknowledgement, media-egress
acknowledgement, paced-egress estimate, or unknown delivery. PSTN delivery is
usually estimated; even browser playback acknowledgement cannot prove human
attention.

## Backpressure

Every in-memory realtime queue has a fixed capacity and an explicit policy.
Depending on the data class, pressure may block a producer briefly, coalesce
replaceable updates, drop explicitly droppable telemetry, degrade an optional
feature, or reject a new session before active sessions collapse.

Final transcripts, authoritative state transitions, and critical tool/call
events cannot be silently discarded.

## Dependency Direction

```text
applications and orchestration
            |
            v
domain rules and provider/persistence interfaces
            ^
            |
adapters: database, LiveKit, providers, external tools
```

Domain and runtime contracts must not import vendor SDKs. Adapters translate
vendor behavior into stable internal types and error categories.

## Initial Technology Direction

These choices are architectural starting points, not performance conclusions:

- Python 3.12+ with `asyncio` for realtime orchestration.
- LiveKit/WebRTC and SIP integration for media transport.
- FastAPI for control-plane HTTP APIs.
- PostgreSQL for durable relational truth and fencing authority.
- Redis for ephemeral coordination.
- S3-compatible storage for recordings and large artifacts.
- OpenTelemetry-compatible signals for observability.

Real providers are introduced only after deterministic contracts and fakes are
working.

