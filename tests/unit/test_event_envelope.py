"""Executable examples for event identity, validation, and wire stability."""

import json
from datetime import UTC, datetime, timedelta, timezone
from typing import cast

import pytest

from voxruntime.domain.identifiers import (
    CallId,
    EventId,
    GenerationId,
    OperationId,
    SessionId,
    TurnId,
    WorkerId,
)
from voxruntime.events.envelope import EventEnvelope
from voxruntime.events.types import DurabilityClass, EventType

SESSION_ID = SessionId.parse("11111111-1111-4111-8111-111111111111")
EVENT_ID = EventId.parse("22222222-2222-4222-8222-222222222222")
OCCURRED_AT = datetime(2026, 9, 26, 10, 30, tzinfo=UTC)


def example_event(**changes: object) -> EventEnvelope:
    """Construct a deterministic envelope and allow named test overrides.

    Solution category:
        Test-data builder pattern that keeps unrelated fixture fields stable.

    Complexity:
        O(k + n) time and space, where ``k`` is the fixed envelope field count
        and ``n`` is the number of nested payload values copied by the envelope.
    """
    fields: dict[str, object] = {
        "event_id": EVENT_ID,
        "schema_version": 1,
        "event_type": EventType.STT_FINAL,
        "durability_class": DurabilityClass.DIAGNOSTIC,
        "session_id": SESSION_ID,
        "sequence_number": 7,
        "occurred_at": OCCURRED_AT,
        "payload": {"transcript": "hello", "confidence": 0.98},
    }
    fields.update(changes)
    return EventEnvelope(**fields)  # type: ignore[arg-type]


def test_create_derives_registry_durability_and_new_event_identity() -> None:
    """Producers choose an event type while the registry supplies its policy."""
    first = EventEnvelope.create(
        event_type=EventType.TOOL_DISPATCHED,
        session_id=SESSION_ID,
        sequence_number=1,
    )
    second = EventEnvelope.create(
        event_type=EventType.TOOL_DISPATCHED,
        session_id=SESSION_ID,
        sequence_number=2,
    )

    assert first.durability_class is DurabilityClass.CRITICAL
    assert first.event_id != second.event_id


def test_payload_is_defensively_copied_and_deeply_immutable() -> None:
    """Caller mutation cannot alter an event after construction."""
    source = {"words": ["hello", "world"]}
    event = example_event(payload=source)

    source["words"].append("changed")

    assert event.payload["words"] == ("hello", "world")
    with pytest.raises(TypeError):
        event.payload["new"] = "value"  # type: ignore[index]


def test_serialization_is_deterministic_and_round_trips() -> None:
    """Equivalent insertion order produces one wire form and identity survives."""
    first = example_event(payload={"b": 2, "a": [1, True, None]})
    second = example_event(payload={"a": [1, True, None], "b": 2})

    serialized = first.to_json()
    restored = EventEnvelope.from_json(serialized)

    assert serialized == second.to_json()
    assert restored == first
    assert restored.event_id == EVENT_ID
    assert restored.to_json() == serialized


def test_all_optional_correlation_identities_round_trip() -> None:
    """Call, turn, generation, operation, worker, epoch, and clock data survive."""
    event = example_event(
        call_id=CallId.parse("33333333-3333-4333-8333-333333333333"),
        turn_id=TurnId.parse("44444444-4444-4444-8444-444444444444"),
        generation_id=GenerationId.parse("55555555-5555-4555-8555-555555555555"),
        operation_id=OperationId.parse("66666666-6666-4666-8666-666666666666"),
        worker_id=WorkerId.parse("77777777-7777-4777-8777-777777777777"),
        ownership_epoch=3,
        clock_domain="worker-monotonic",
        monotonic_offset_ns=50,
    )

    assert EventEnvelope.from_json(event.to_json()) == event


def test_timestamp_is_serialized_as_normalized_utc() -> None:
    """Equivalent wall-clock instants have one canonical UTC representation."""
    offset_time = datetime(
        2026, 9, 26, 16, 0, tzinfo=timezone(timedelta(hours=5, minutes=30))
    )

    serialized = example_event(occurred_at=offset_time).to_json()

    assert '"occurred_at":"2026-09-26T10:30:00.000000Z"' in serialized


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"schema_version": 2}, "unsupported schema_version"),
        ({"sequence_number": 0}, "sequence_number must be >= 1"),
        ({"sequence_number": True}, "sequence_number must be an integer"),
        ({"ownership_epoch": 0}, "ownership_epoch must be >= 1"),
        ({"occurred_at": datetime(2026, 9, 26)}, "timezone-aware"),
        ({"clock_domain": "worker"}, "provided together"),
        ({"monotonic_offset_ns": 1}, "provided together"),
        ({"clock_domain": " ", "monotonic_offset_ns": 1}, "must not be blank"),
        ({"payload": cast(dict[str, object], [])}, "payload must be a JSON object"),
        ({"payload": {"bad": float("nan")}}, "non-finite"),
        ({"payload": {"bad": {1, 2}}}, "unsupported type set"),
    ],
)
def test_invalid_envelope_values_fail(change: dict[str, object], message: str) -> None:
    """Invalid scalar, clock, schema, and payload values fail at the boundary."""
    with pytest.raises((TypeError, ValueError), match=message):
        example_event(**change)


def test_durability_must_match_the_registry() -> None:
    """A producer cannot downgrade a critical event to droppable telemetry."""
    with pytest.raises(ValueError, match="requires durability A"):
        example_event(
            event_type=EventType.TOOL_DISPATCHED,
            durability_class=DurabilityClass.HIGH_VOLUME,
        )


@pytest.mark.parametrize(
    "serialized",
    [
        '{"event_id":"one","event_id":"two"}',
        "[]",
        '{"value":NaN}',
    ],
)
def test_malformed_or_non_envelope_json_is_rejected(serialized: str) -> None:
    """Duplicate keys, wrong roots, and non-standard numbers cannot enter."""
    with pytest.raises((TypeError, ValueError)):
        EventEnvelope.from_json(serialized)


def test_unknown_and_missing_wire_fields_are_rejected() -> None:
    """Schema drift cannot be silently discarded during deserialization."""
    decoded = json.loads(example_event().to_json())
    del decoded["worker_id"]
    decoded["unexpected"] = "value"

    with pytest.raises(ValueError, match=r"missing=.*worker_id.*unknown=.*unexpected"):
        EventEnvelope.from_json(json.dumps(decoded))


def test_direct_construction_enforces_runtime_identity_types() -> None:
    """Untyped callers cannot pass a string where SessionId is required."""
    wrong_type = cast(SessionId, "not-a-session-id")

    with pytest.raises(TypeError, match="session_id must be SessionId"):
        example_event(session_id=wrong_type)
