# Glossary

Terms in this file have precise project meanings. Code, tests, events, and
documentation should use them consistently.

For worked explanations and exercises, read [Foundations](foundations.md).
Use this page to look up a term; use the handbook to understand the mechanism.
Expand each new acronym in its lesson and add it here before relying on it.

## Foundation Vocabulary and Reading Map

| Term | Plain meaning | Deeper explanation |
|---|---|---|
| Source code | Text expressing program instructions | Foundations §1 |
| CPU | Processor that executes machine instructions | Foundations §1, §5 |
| Operating system (OS) | Software managing processes, memory, and devices | Foundations §1 |
| Shell / terminal | Command interpreter / interface used to interact with it | Foundations §1 |
| Process / thread | Running program instance / execution thread within it | Foundations §1, §6 |
| Interpreter / CPython | Program executing Python / a specific Python implementation | Foundations §1 |
| Bytecode | Intermediate instructions used by an interpreter | Foundations §1 |
| Module / package | Unit of Python code / grouping of modules | Foundations §1 |
| Entry point | Where application execution begins | Foundations §1 |
| Type / object / reference | Behavior category / runtime value / link to a value | Foundations §2 |
| Mutable / immutable | Can / cannot change its value in place | Foundations §2 |
| Annotation | Stated type intent, not automatic runtime validation | Foundations §2 |
| Function / parameter / argument | Named operation / input name / supplied input value | Foundations §3 |
| Exception / traceback | Error-control signal / recorded path of calls | Foundations §3 |
| Side effect | Change beyond returning a value | Foundations §3, §9 |
| Algorithm / data structure | Procedure / organization of data | Foundations §4 |
| Big-O / auxiliary space | Growth bound / additional working memory | Foundations §4 |
| Allocation / lifetime | Reserving object storage / interval data remains relevant or retained | Foundations §5 |
| RSS | Resident set size: resident process memory | Foundations §5 |
| Coroutine / task / event loop | Suspendable computation / scheduled execution / coordinator | Foundations §6 |
| Concurrency / parallelism | Overlapping work lifetimes / simultaneous execution | Foundations §6 |
| I/O | Input/output through devices or communication boundaries | Foundations §6, §8 |
| Producer / consumer | Component creating / processing items | Foundations §7 |
| Queue / buffer | Waiting-work structure / temporary data storage | Foundations §7 |
| API | Agreed interface for calling an operation | Foundations §8 |
| HTTP / JSON | Request-response protocol / data representation format | Foundations §8 |
| Serialization | Converting values to a transferable representation | Foundations §8 |
| Socket | OS communication interface | Foundations §8 |
| Authentication / authorization | Establishing identity / checking permitted actions | Foundations §8 |
| Tenant | Organization/customer boundary in a shared system | Foundations §8 |
| Schema / index | Data structure and constraints / lookup aid | Foundations §9 |
| SQL | Language for defining and querying relational data | Foundations §9; detailed Phase 4 lesson planned |
| Transaction / commit | Grouped database operation / making its changes effective | Foundations §9 |
| Attempt | One send belonging to a logical operation | Foundations §9 |
| State / invariant | Relevant condition / property that must remain true | Foundations §10 |
| Sample / sample rate | One signal measurement / measurements per second per channel | Foundations §11 |
| PCM / bit depth | Direct numerical sample representation / bits per sample | Foundations §11 |
| Frame / codec | Short audio group / audio encoding-decoding mechanism | Foundations §11 |
| STT / TTS | Speech-to-text / text-to-speech | Foundations §12 |
| LLM | Large language model | Foundations §13 |
| Token / context | Model input unit / information supplied for a generation | Foundations §13 |
| Training / inference | Adjusting model parameters / applying a trained model | Foundations §13 |
| Embedding / RAG | Numerical representation / retrieval-augmented generation | Foundations §13 |
| Fake / fixture | Controlled substitute / reusable test setup or data | Foundations §14 |
| Metric / log / trace | Measurement / event record / connected operation history | Foundations §14 |
| Latency / throughput | Time between boundaries / completed work per unit time | Foundations §15 |
| p50 / p95 / p99 | Distribution percentiles, not averages or worst-case guarantees | Foundations §15 |
| Benchmark / profiler | Controlled workload / tool locating resource use | Foundations §15 |
| Dependency / virtual environment | Required package / isolated Python package environment | Foundations §16 |
| Git / commit / CI | Version control / recorded snapshot / automated checks | Foundations §16 |
| UUID | Universally unique identifier; a fixed-width 128-bit identity value | Checkpoint 0.1 walkthrough |
| Dataclass | Python class helper that generates common value-object methods | Checkpoint 0.1 walkthrough |
| `frozen` / `slots` | Dataclass options restricting assignment / declaring instance storage | Checkpoint 0.1 walkthrough |
| TOML | Configuration format used by `pyproject.toml` | Checkpoint 0.1 walkthrough |
| Lockfile | Record of selected dependency versions for repeatable environments | Foundations §16; ADR-0001 |
| AST | Abstract syntax tree: structured representation of parsed source | Checkpoint 0.1 architecture test |

## Project Terms to Teach Before Use

These definitions identify the role; each needs a worked lesson before its
implementation. Product names do not substitute for understanding the mechanism.

| Term | Role and first teaching point |
|---|---|
| WebRTC | Technologies for realtime browser media; Phase 1 transport lesson |
| LiveKit | Selected media infrastructure providing transport capabilities; explain its boundary in Phase 1 |
| SIP | Session Initiation Protocol for establishing/managing communication sessions; Phase 5 |
| PSTN | Public Switched Telephone Network; ordinary phone-call channel, Phase 5 |
| RTP | Real-time Transport Protocol carrying media packets; Phase 5 |
| DTMF | Dual-tone multi-frequency keypad signaling; Phase 5 |
| PostgreSQL | Relational database selected for durable truth; Phase 4 |
| Redis | Data store selected for ephemeral coordination; Phase 6 |
| FastAPI | Python framework for HTTP APIs; Phase 4 |
| S3-compatible storage | Object storage addressed through an S3-compatible API; recording lessons |
| Outbox | Durable pending-event records committed with the originating change; Phase 4 |
| Projection | Derived read representation rebuilt from authoritative data/events; Phase 4 |
| Circuit breaker | Temporarily prevents calls to a failing dependency; Phase 9 |
| Bulkhead | Resource boundary limiting one workload's effect on others; Phase 9 |
| SLI / SLO | Service-level indicator / objective for that measurement; operational lessons |
| RPO / RTO | Recovery point objective (data-loss window) / recovery time objective; recovery lessons |
| RBAC | Role-based access control; authorization lessons |
| TTFT / TTFB | Time to first token / first byte, with explicit measurement boundaries; Phase 1 |
| GPU | Processor architecture used for highly parallel computation; Phase 10 |
| ADR | Architecture decision record: context, choice, consequences, and revisit triggers |

## How to Expand an Entry

A new concept's lesson must give its expanded name, prerequisite links, plain
meaning, motivating problem, mechanism, concrete example, project location,
common misconception, trade-off, and practice question with explanation.
Record version-specific behavior with a source when implementing it. The
reading map above is initial coverage, not a claim that every term is mastered.

## Agent

A stable logical voice-agent identity. Mutable metadata belongs to the agent;
executable behavior belongs to immutable versions and deployment artifacts.

## Agent Version

An immutable logical revision of agent behavior. A complete deployment also
references immutable tools, policies, knowledge, provider configuration, and
runtime configuration through a deployment artifact.

## Backpressure

Behavior applied when a consumer cannot keep up with its producer. Policies
include bounded waiting, coalescing replaceable updates, dropping explicitly
non-critical data, degrading optional work, or rejecting new sessions.

## Barge-In

A caller beginning to speak while agent output is playing. It invalidates the
old output generation and stops or flushes stale playback within a measured
reaction window.

## Cancellation

A cooperative request for in-process work to stop. Cancellation does not prove
that a remote request stopped and cannot reverse an external side effect.

## Class-A Event

A correctness-critical event requiring recoverable at-least-once handoff and
idempotent consumption. It cannot be silently lost under telemetry pressure.

## Clock Domain

A set of timestamps that may be safely subtracted because they share a clock
and origin. Cross-domain measurements require synchronization and uncertainty
metadata.

## Control Plane

The APIs and storage that define agents, versions, deployments, tools,
credentials, evaluations, and administrative policy. It is not part of the
per-frame live audio path.

## Data Plane

The latency-sensitive runtime that routes and executes live conversations.

## Delivery Evidence

Evidence that synthesized audio progressed through a client or transport. It
may be confirmed by client acknowledgement, confirmed at media egress,
estimated from paced egress, or unknown. It is not proof of human attention.

## Deployment Artifact

An immutable, content-addressed bundle of all behavior-defining references for
a call: agent version, tools, policies, knowledge snapshot, provider settings,
and runtime version.

## Endpointing

The decision that the caller has completed a conversational turn, based on VAD,
silence, STT state, and optionally semantic signals.

## Event-Loop Lag

Delay between when an asyncio callback or task is eligible to run and when the
event loop actually runs it. It reveals overload or blocking work that CPU
percentage alone may hide.

## Fencing

Rejecting an operation from a stale owner by validating its ownership epoch at
the authoritative protected-operation boundary.

## Generation

An identity for a replaceable stream of work. VoxRuntime uses distinct output
and publication generations so stale synthesis/audio and stale publishers can
be rejected independently.

## Idempotency Key

A stable identifier for one intended logical action. Reusing the same key for
the same action returns or reconciles the existing operation rather than
creating a duplicate side effect.

## Lease

Ephemeral liveness and routing state, typically with a TTL. A lease is not the
durable source of monotonic ownership authority.

## Logical Operation

One intended business side effect, which may involve multiple network attempts
or later reconciliation. It is identified by a stable operation identity.

## Monotonic Clock

A clock suitable for measuring elapsed time because it does not move backward
when wall-clock time is adjusted.

## Ownership Epoch

A durable, monotonically increasing fencing token for a session. Only the
current epoch may perform protected operations.

## Publication Generation

The media-layer authority identifying the sole agent-audio publisher admitted
for a call.

## Reconciliation

Recovery work that gathers evidence to resolve an incomplete or ambiguous
operation without blindly repeating it.

## SessionRuntime

The per-call in-memory orchestrator for media, speech processing, turns,
reasoning, tools, synthesis, playback, cancellation, and telemetry.

## Structured Concurrency

A concurrency model in which child tasks live inside an explicit owning scope,
and completion, failure, or cancellation joins and cleans up those tasks.

## Turn Epoch

An identity/version used to determine whether asynchronous results still belong
to the current conversational turn.

## UNKNOWN

A certainty classification meaning an external side effect may have committed
but the platform lacks authoritative evidence of success or failure. It
requires reconciliation, compensation, or human review.

## Voice Activity Detection (VAD)

Detection of speech start, continuation, and stop. VAD supports interruption
and endpointing but is not itself proof that a semantic turn is complete.
