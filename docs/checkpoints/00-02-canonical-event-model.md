# Checkpoint 0.2: Canonical Event Model

## Status

`COMPLETE` (engineering evidence recorded 2026-09-26; learner practice remains
`not assessed`)

## Learning Objectives

After this checkpoint, the learner should be able to explain:

- why distributed components need one event vocabulary;
- the difference between an event type, envelope, payload, and registry;
- why event identity differs from delivery-attempt identity;
- what at-least-once delivery requires from a consumer;
- how schema versions make compatibility decisions explicit;
- how JSON serialization crosses a process boundary;
- why frozen dataclasses do not automatically freeze nested objects;
- why wall-clock and monotonic-clock metadata have different purposes;
- how durability classes change behavior during failure or overload.

## Learner Starting Point and Prerequisites

Read Foundations sections 2-4, 8, 10, 14, and 15. Checkpoint 0.1 introduced
Python modules, functions, dataclasses, UUIDs, runtime validation, tests, and
dependency boundaries. Learner understanding remains `not assessed` until an
exercise or explanation provides evidence.

New vocabulary is recorded in the project glossary: event, envelope, payload,
serialization, enum, schema version, at-least-once delivery, durability class,
aggregate sequence, and duplicate delivery.

## System Context

During a call, many activities occur in different components: speech starts,
transcripts arrive, tools dispatch, audio plays, and ownership changes. Later,
operators and recovery workers need to answer what happened. They cannot do so
if every producer uses different names or silently omits identity and ordering
metadata.

```text
producer
  -> constructs EventEnvelope using EVENT_REGISTRY policy
  -> serializes explicit schema to JSON
  -> transport or durable store (implemented later)
  -> consumer deserializes and validates
  -> consumer deduplicates Class-A processing by event_id (implemented later)
```

This checkpoint defines the object and wire contract. It does not implement an
event broker, outbox, database, network transport, consumer deduplication table,
or exactly-once delivery.

## Teaching Slices

1. **Vocabulary:** compare a free-form dictionary with an `EventType` enum and
   demonstrate how a spelling difference breaks consumers.
2. **Identity and durability:** create two events and distinguish a new logical
   event from redelivery of an existing `event_id`.
3. **Envelope validation:** construct valid metadata, then break schema,
   durability, timestamp, sequence, and clock-pair invariants.
4. **Serialization:** trace domain objects into JSON primitives and back.
5. **Nested immutability:** mutate a producer-owned list after construction and
   observe that the event retains its original tuple copy.
6. **Resources:** run 10,000 local round trips and interpret time, wire size,
   and traced allocations with the benchmark limitations.

## Problem and Failure Without the Contract

A producer could emit `TOOL_COMPLETE`, while a recovery consumer expects
`TOOL_SUCCEEDED`. One worker could label a dispatched tool as droppable Class C.
A JSON parser could silently accept duplicate `event_id` keys and keep only the
last. A producer could reuse a mutable payload and accidentally rewrite an event
after emission. A consumer could accept a newer schema while ignoring fields it
does not understand.

Each case creates plausible but inconsistent history. The envelope makes these
conditions fail at a named boundary.

## Contract and Invariants

- `EventType` contains exactly the 55 names in design Appendix A.
- `EVENT_REGISTRY` is the single mapping from type to meaning and durability.
- Every envelope has an `EventId`, supported schema version, `SessionId`,
  positive sequence number, aware wall-clock timestamp, and JSON-object payload.
- Durability is derived from and must match the registry.
- Optional correlation identities retain their distinct domain types.
- Ownership epochs are positive when present.
- Monotonic offset and clock domain appear together or are both absent.
- Payload keys are strings; numbers are finite; nested data is copied and frozen.
- Serialization emits all schema fields; deserialization rejects missing or
  unknown fields and duplicate JSON keys.
- Serialization preserves the logical `event_id`. Creating another event
  creates another ID.
- Sequence numbers describe per-session aggregate order; they do not promise
  transport arrival order.

## Durability Classes

| Class | Meaning | Pressure/failure behavior | Examples |
|---|---|---|---|
| A: critical | Needed for correctness, recovery, authority, outcome, or billing truth | Recoverable at-least-once handoff; consumers must be idempotent | `TOOL_DISPATCHED`, `CALL_ENDED`, `STALE_OWNER_FENCED` |
| B: diagnostic | Important lifecycle evidence | Asynchronous bounded persistence/retry | `STT_FINAL`, `LLM_COMPLETED`, `TTS_ERROR` |
| C: high volume | Frequent, replaceable observation | May be sampled/coalesced/dropped before harming live media | `STT_PARTIAL`, `AUDIO_PLAYBACK_PROGRESS`, `QUEUE_PRESSURE` |

The complete assignment is in `EVENT_REGISTRY` and justified by ADR-0003.
Persistence behavior begins in later checkpoints; this class is policy metadata
today.

## Files and Symbols

| File/symbol | Purpose | Tests | Resource notes |
|---|---|---|---|
| `domain.identifiers.UUIDIdentifier` | Shared UUID parsing/generation/runtime invariant | Existing identity tests | Fixed-width domain value |
| `CallId`, `TurnId`, `EventId`, `GenerationId`, `OperationId`, `WorkerId` | Prevent correlation identities from being interchanged | Type and inequality tests | One UUID per instance |
| `events.types.DurabilityClass` | Stable A/B/C names | Registry representative tests | Three process-lifetime enum members |
| `events.types.EventType` | Appendix A vocabulary | Registry set equality and count | 55 process-lifetime enum members |
| `events.registry.EventDefinition` | Immutable durability and meaning | Registry tests | Fixed two-field record |
| `EVENT_REGISTRY` | Read-only canonical lookup | Completeness/read-only tests | O(55) fixed retained mapping |
| `_freeze_json` | Validate and make a defensive immutable payload copy | Nested mutation and invalid payload tests | O(n) copy, O(d) recursion |
| `_thaw_json` | Create detached JSON containers | Round-trip tests | O(n) copy, O(d) recursion |
| `_parse_json_object` | Reject duplicate keys | Malformed JSON tests | Average O(k) for k pairs |
| `_reject_json_constant` | Reject NaN/Infinity tokens | Malformed JSON tests | Scalar validation |
| `_optional_identifier` | Preserve concrete optional ID types while parsing | Full-correlation round trip | O(text length), bounded UUID input |
| `_required_int` | Reject booleans/non-integers and enforce a lower bound | Parametrized invalid tests | O(1) |
| `EventEnvelope.__post_init__` | Enforce all cross-field invariants and freeze payload | Invalid/immutability tests | O(n) payload time/space |
| `EventEnvelope.create` | Generate current schema/event ID and derive durability | Factory tests | O(n) payload copy |
| `EventEnvelope.to_dict` | Explicit domain-to-wire projection | Round-trip tests | O(n) detached payload copy |
| `EventEnvelope.to_json` | Deterministic compact serialization | Insertion-order test | Output O(n), key sorting |
| `EventEnvelope.from_json` | Strict untrusted boundary parser | Invalid/schema/round-trip tests | O(n+d) parse/validation space |
| `tools/benchmark_events.py` functions | CLI validation and repeatable round-trip measurement | Quality gates and manual run | O(i*n), tracing overhead |

Here, `n` is total nested payload/wire values, `d` is maximum nesting depth,
`k` is object pair count, and `i` is benchmark iterations.

## Python and Runtime Walkthrough

### Enums and Registry

`StrEnum` gives members both enum identity and string values. Internal code can
require `EventType.STT_FINAL`; JSON contains `"STT_FINAL"`. The dictionary gives
average O(1) lookup, and `MappingProxyType` presents a read-only view. Each
`EventDefinition` is frozen, so callers cannot modify a definition's fields.

The module builds a private dictionary once during import and exposes its proxy.
Python privacy for an underscore name is a convention, so the stronger contract
comes from using the public proxy and tests/review. No security boundary is
claimed.

### Strong Identity Inheritance

`UUIDIdentifier` holds shared behavior. Empty frozen dataclass subclasses create
separate runtime types without duplicating parsing code. Dataclass equality
requires matching concrete class, so the same UUID wrapped as `SessionId` and
`EventId` does not compare equal.

The optional-ID helper uses Python 3.12 generic function syntax. The `[T: Base]`
part declares `T` with an upper bound before the ordinary function parameters.
This tells mypy that passing `type[CallId]` returns `CallId | None`, rather than
an imprecise union of all IDs.

### Frozen Is Shallow

`frozen=True` stops `event.payload = ...`; it does not stop mutation of a list
inside the payload. `_freeze_json` performs a depth-first copy. Dictionaries
become fresh read-only mappings and lists become tuples. Scalar JSON values are
immutable or treated as values. The producer can mutate its original containers
without changing event history.

Because the dataclass is already in frozen initialization, `__post_init__` uses
`object.__setattr__` once to replace the input with the validated frozen copy.
This controlled bypass establishes the invariant; ordinary callers still get a
frozen object.

### JSON Boundary

JSON has objects, arrays, strings, numbers, booleans, and null. Python uses
dictionaries, lists, strings, integers/floats, booleans, and `None` for them.
UUIDs, enums, and datetimes are not JSON primitives, so `to_dict` explicitly
converts them.

`sort_keys=True` removes dictionary insertion order from emitted text;
`separators=(",", ":")` removes optional spaces; `allow_nan=False` rejects
non-standard float values; `ensure_ascii=False` preserves Unicode characters.
The timestamp is normalized to UTC with microseconds and a `Z` suffix.

Deserialization uses `object_pairs_hook` because an ordinary decoded dictionary
has already lost evidence of duplicate keys. The hook sees ordered key/value
pairs and rejects a second occurrence. Exact top-level field comparison prevents
silently ignored schema drift.

This is deterministic within the declared Python wire contract. It is not a
claim of conformance to an external cryptographic canonical-JSON standard.

### Event Identity and At-Least-Once Delivery

Serialization and deserialization preserve `event_id`. A later transport may
deliver the same serialized event twice. An idempotent Class-A consumer must
record or otherwise recognize the event ID so applying it twice has the same
authoritative effect as applying it once. This checkpoint models the identity;
the durable deduplication mechanism is not implemented yet.

## Concrete Data Flow

```text
EventEnvelope.create(STT_FINAL, session, sequence=7, payload)
  -> registry lookup yields Class B
  -> EventId.new obtains UUID randomness
  -> __post_init__ validates IDs/scalars/clocks
  -> _freeze_json copies dict/list into proxy/tuple
  -> to_dict converts IDs/enums/time and thaws payload copy
  -> json.dumps emits deterministic text
  -> EventEnvelope.from_json parses pairs and validates exact schema
  -> UUID/enum/datetime primitives become typed values
  -> __post_init__ applies the same invariants and freezes again
```

No database, socket, thread, or async task is involved. Serialization allocates
a detached representation and output string. Deserialization allocates parsed
containers, typed identity objects, and a frozen payload copy.

## Tests and Failure Evidence

The suite grew from 9 to 37 tests. It covers:

- 55 enum/registry entries with no missing or extra type;
- representative Class A/B/C policy and registry immutability;
- generated event identity and registry-derived durability;
- defensive deep copying and mutation rejection;
- deterministic JSON despite different insertion order;
- full optional correlation identity round trips;
- timezone normalization;
- unsupported schema, zero/bool sequence, invalid epoch, naive timestamp,
  incomplete/blank clock metadata, invalid payload root/type, and NaN;
- durability downgrade rejection;
- duplicate JSON keys, non-object roots, non-standard numbers, unknown/missing
  fields, and untyped identity misuse;
- distinct domain identity types wrapping the same UUID.

The tests do not prove every possible payload depth/size, database deduplication,
transport ordering, crash recovery, or cross-language JSON compatibility.

## Resource Evidence

Command:

```bash
make benchmark-events
```

One measured run on the workspace's CPython 3.12.13 performed 10,000 complete
serialize/deserialize cycles of a 560-byte representative event:

- wall time: approximately 3.081 seconds;
- process CPU time: approximately 3.058 seconds;
- throughput: approximately 3,246 round trips/second;
- peak Python memory traced during the loop: 145,414 bytes.

`tracemalloc` adds significant overhead, the loop is sequential, and the
payload is one fixed example. This microbenchmark helps us understand cost; it
is not a worker capacity result or production SLO. A production workload will
include different payloads, I/O, concurrency, buffering, and native libraries.

## Exercises

### Prompts

1. Predict whether changing the source payload list after envelope construction
   changes serialized JSON. Explain before running the test.
2. Change `STT_PARTIAL` durability locally from C to A. Which test detects it,
   and why should this be an architectural decision rather than producer choice?
3. Remove `sort_keys=True`, construct equivalent payload dictionaries in two
   insertion orders, and diagnose the changed test output. Restore it afterward.
4. Imagine a Class-A `TOOL_SUCCEEDED` event is delivered twice. Describe what
   this checkpoint guarantees and what a future consumer must still implement.
5. Apply the same model to an order system: define one logical `ORDER_PAID`
   event and distinguish it from two queue delivery attempts.

### Hints

1. Follow the input through `_freeze_json`; identify which object is retained.
2. The representative policy test asserts registry ownership of each behavior.
3. Python dictionaries preserve insertion order, while equivalent JSON objects
   need not arrive with the same construction history.
4. Look for identity persistence versus consumer-side state.
5. Use one event ID for the fact and separate broker metadata for attempts.

### Worked Explanations

1. The event does not change. Construction copies the list into a tuple inside a
   new mapping. Mutating the producer's list affects only the producer's object.
2. `test_registry_represents_each_durability_behavior` fails. Durability decides
   whether loss is permissible, so local downgrade could break recovery truth.
3. Without sorted keys, insertion order affects emitted text. The values remain
   semantically equivalent JSON objects, but byte/string determinism is lost.
4. The preserved event ID lets a consumer recognize sameness. This checkpoint
   does not store processed IDs or make the consumer's mutation idempotent.
5. `ORDER_PAID` has one stable logical ID. Queue attempt numbers can change while
   redelivering that same fact; a new payment fact requires a new event ID.

## Decisions and Trade-offs

[ADR-0003](../adr/0003-canonical-event-contract.md) records the event model,
durability assignments, JSON choice, alternatives, limitations, and revisit
triggers. Typed per-event payload schemas are deferred until their owning
checkpoints define real payload semantics.

## Exit Criteria

- [x] `EventEnvelope`, `EventType`, and `DurabilityClass` are executable types.
- [x] All Appendix A names exist in one registry.
- [x] Events serialize and deserialize deterministically.
- [x] Invalid envelopes and schema drift fail at the boundary.
- [x] Logical event identity survives round trips.
- [x] Durability cannot be selected independently by a producer.
- [x] Payloads are defensively immutable after construction.
- [x] Formatting, linting, strict typing, and 37 tests pass.
- [x] Complexity, runtime behavior, limitations, and measurement are documented.
- [x] Learner exercises and worked explanations are available.

## Learning Status

Engineering implementation and teaching material are complete. Learner
prediction, debugging, explanation, and independent transfer remain
`not assessed` until the learner provides evidence.

## Open Questions for Later Checkpoints

- Which events receive typed payload schemas first?
- What payload size/depth limits belong at public ingestion boundaries?
- Which durable store implements Class-A idempotent consumer records?
- Does cross-language interoperability justify a generated schema format?
- How will schema version 2 migrate historical events if introduced?
