# ADR-0003: Canonical Event Envelope, Registry, and Durability Policy

- Status: Accepted
- Date: 2026-09-26
- Deciders: VoxRuntime maintainers
- Related checkpoint: 0.2

## Context

Realtime workers, persistence, recovery, telemetry, and evaluation will exchange
events. If each component invents names, fields, or durability independently,
historical calls cannot be reconstructed reliably and safety-critical events
can be treated like droppable telemetry.

The design document makes Appendix A canonical, requires versioned envelopes,
assumes at-least-once delivery for Class-A events, and does not assume arrival
order across transports.

## Decision Drivers

- Keep one event vocabulary shared by producers, consumers, tests, and docs.
- Preserve logical event identity across serialization and redelivery.
- Make schema incompatibility fail explicitly.
- Keep an emitted event stable even if the producer mutates its input objects.
- Encode A/B/C pressure policy per event type.
- Avoid infrastructure or third-party serialization dependencies in Phase 0.

## Considered Options

1. Explicit Python enums, registry, immutable envelope, and strict JSON codec.
2. Free-form dictionaries with naming conventions.
3. Protocol Buffers or another generated binary schema immediately.
4. Separate event classes for all 55 event types immediately.

## Decision

Use `EventType` for the 55 Appendix A names and a read-only `EVENT_REGISTRY`
mapping each name to meaning and durability. `EventEnvelope` contains schema,
identity, ordering, wall-clock, optional monotonic-clock, correlation, and JSON
payload fields.

Schema version 1 is the only accepted version. Serialization explicitly emits
every field as compact UTF-8-compatible JSON with sorted object keys, six-digit
UTC timestamps, and standard finite JSON numbers. Deserialization rejects
unknown/missing fields, duplicate object keys, non-standard numbers, unknown
enum values, invalid identities, and unsupported schema versions.

Payload mappings and arrays are defensively copied into mapping proxies and
tuples. Serialization thaws them into fresh JSON-compatible containers.

## Durability Assignment

Class A contains call truth needed for terminal reconstruction, tool dispatch
and outcomes, ownership/publication safety, usage finalization, critical-event
recovery, and transfer outcomes. Class B contains diagnostic lifecycle
boundaries. Class C contains high-frequency/coalescible partials, queue samples,
renewals, and playback progress.

The design gives behavior and representative examples rather than a complete
per-event table. ADR-0003 makes the initial complete mapping explicit in code.
Changing a class is a policy/schema review, not a producer-local choice.

## Why This Option

Explicit code is inspectable while the contract is still being learned. Strict
JSON provides human-readable evidence and exercises boundary validation without
selecting a production event transport. One generic envelope avoids creating 55
payload schemas before their producing checkpoints define real data.

Free-form dictionaries cannot enforce vocabulary or cross-field rules. A binary
schema may later improve cross-language compatibility and size, but adopting it
now would add generation/tooling concepts before payload contracts exist.

## Consequences

### Positive

- Registry completeness is executable and tested.
- Producers cannot downgrade an event's durability.
- Same logical event ID survives serialization and redelivery.
- Caller mutation cannot alter a constructed event payload.
- Wire-format changes are visible in explicit projection code.

### Negative

- JSON has representation and size overhead.
- Payload semantics remain event-specific and will need schemas later.
- The recursive freezer can hit Python's recursion limit on maliciously deep
  input; external API boundaries must eventually enforce document depth/size.
- Sorted-key JSON is deterministic for this implementation contract but is not
  claimed to implement an external canonical-JSON standard.

### Risks and Mitigations

- Producers may emit payloads with inconsistent meaning. Add typed payload
  contracts alongside the checkpoint that owns each event.
- Schema version 2 would currently be rejected. Add an explicit decoder/migrator
  before producing a new version.
- Python enum/registry changes can break stored data. Compatibility tests and
  migration notes are required before changing existing values.

## Python/Runtime Implications

`frozen=True` prevents ordinary dataclass attribute assignment but does not
deep-freeze dictionaries or lists. `EventEnvelope.__post_init__` therefore makes
a validated immutable copy and uses `object.__setattr__` only while establishing
the frozen object's invariant.

`StrEnum` members behave as stable strings at the JSON edge while retaining
distinct enum types internally. The generic optional-identifier parser uses
Python 3.12 type-parameter syntax so mypy preserves each returned identity type.

## Complexity and Resource Implications

For `n` nested payload values and nesting depth `d`, construction and thawing
use O(n) time, O(n) retained copy space, and O(d) recursion stack. JSON encoding
adds output-size space and key-sorting work. The registry holds 55 fixed frozen
definitions for the process lifetime.

## Validation

Tests cover all registry entries, each durability behavior, defensive copying,
round trips, deterministic output, identities, timestamps, invalid fields,
clock pairs, duplicate keys, non-finite numbers, and schema mismatch.

## Revisit Triggers

- A second schema version is designed.
- Cross-language consumers require a generated schema.
- Measured serialization cost or event size materially affects the runtime.
- Typed payload definitions become stable enough to register per event.

