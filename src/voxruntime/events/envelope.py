"""Validated, immutable, deterministically serialized runtime event envelope."""

import json
import math
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from types import MappingProxyType
from typing import Any, Self

from voxruntime.domain.identifiers import (
    CallId,
    EventId,
    GenerationId,
    OperationId,
    SessionId,
    TurnId,
    UUIDIdentifier,
    WorkerId,
)
from voxruntime.events.registry import EVENT_REGISTRY
from voxruntime.events.types import DurabilityClass, EventType

CURRENT_SCHEMA_VERSION = 1
SUPPORTED_SCHEMA_VERSIONS = frozenset({CURRENT_SCHEMA_VERSION})

_SERIALIZED_FIELDS = frozenset(
    {
        "event_id",
        "schema_version",
        "event_type",
        "durability_class",
        "session_id",
        "call_id",
        "turn_id",
        "ownership_epoch",
        "generation_id",
        "operation_id",
        "worker_id",
        "sequence_number",
        "occurred_at",
        "clock_domain",
        "monotonic_offset_ns",
        "payload",
    }
)


def _freeze_json(value: object, *, path: str = "payload") -> object:
    """Validate and recursively freeze a value from the JSON data model.

    Args:
        value: Candidate scalar, mapping, list, or tuple.
        path: Human-readable location used in validation errors.

    Returns:
        Scalars unchanged, arrays as tuples, and objects as read-only mappings.

    Raises:
        TypeError: If a key is not text or a value is outside the JSON model.
        ValueError: If a floating-point value is not finite.

    Solution category:
        Depth-first recursive validation and immutable transformation.

    Complexity:
        O(n) time and O(n + d) space, where ``n`` is the total number of values
        and ``d`` is maximum nesting depth. O(n) is retained by the frozen copy;
        O(d) is recursion-stack space.
    """
    # 1. Preserve JSON scalar values while rejecting non-finite floats.
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"{path} contains a non-finite number")
        return value

    # 2. Copy JSON objects into a fresh mapping before making it read-only.
    if isinstance(value, Mapping):
        frozen: dict[str, object] = {}
        for key, child in value.items():
            if not isinstance(key, str):
                raise TypeError(f"{path} object keys must be strings")
            frozen[key] = _freeze_json(child, path=f"{path}.{key}")
        return MappingProxyType(frozen)

    # 3. Convert mutable JSON arrays into immutable tuples.
    if isinstance(value, (list, tuple)):
        return tuple(
            _freeze_json(child, path=f"{path}[{index}]")
            for index, child in enumerate(value)
        )

    raise TypeError(f"{path} contains unsupported type {type(value).__name__}")


def _thaw_json(value: object) -> object:
    """Convert frozen payload containers into structures accepted by JSON.

    Solution category:
        Depth-first recursive representation transformation.

    Complexity:
        O(n) time and O(n + d) space for ``n`` nested values and depth ``d``.
    """
    if isinstance(value, Mapping):
        return {key: _thaw_json(child) for key, child in value.items()}
    if isinstance(value, tuple):
        return [_thaw_json(child) for child in value]
    return value


def _parse_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Reject duplicate JSON object keys instead of silently keeping one.

    Solution category:
        Single-pass validation and dictionary construction.

    Complexity:
        Average O(n) time and O(n) space for ``n`` key/value pairs, relying on
        Python dictionary average-case membership lookup.
    """
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def _reject_json_constant(value: str) -> object:
    """Reject non-standard JSON constants such as NaN and Infinity.

    Solution category:
        Parser callback enforcing the standard JSON numeric domain.

    Complexity:
        O(n) time for constant text length ``n`` and O(1) auxiliary space.
    """
    raise ValueError(f"invalid JSON number: {value}")


def _optional_identifier[IdentifierT: UUIDIdentifier](
    raw: object, identifier_type: type[IdentifierT]
) -> IdentifierT | None:
    """Parse an optional UUID identity from an untrusted decoded value.

    Solution category:
        Boundary validation and parsing.

    Complexity:
        O(n) time for input text length ``n`` and O(1) auxiliary space because
        valid UUID text has bounded size.
    """
    if raw is None:
        return None
    if not isinstance(raw, str):
        raise TypeError(f"{identifier_type.__name__} must be text or null")
    return identifier_type.parse(raw)


def _required_int(raw: object, *, name: str, minimum: int) -> int:
    """Validate a decoded integer field without accepting booleans.

    Solution category:
        Constant-time scalar boundary validation; no algorithm applies.

    Complexity:
        O(1) time and O(1) auxiliary space.
    """
    if isinstance(raw, bool) or not isinstance(raw, int):
        raise TypeError(f"{name} must be an integer")
    if raw < minimum:
        raise ValueError(f"{name} must be >= {minimum}")
    return raw


@dataclass(frozen=True, slots=True)
class EventEnvelope:
    """Carry one canonical event plus correlation and ordering metadata.

    The event ID identifies the logical event across at-least-once redelivery.
    The per-session sequence number supports aggregate ordering but does not
    imply that transports deliver events in order.

    Complexity:
        Construction is O(n) time and retained space for ``n`` payload values
        because payload data is validated and copied into immutable containers.
        Scalar metadata has fixed-size domain cost.
    """

    event_id: EventId
    schema_version: int
    event_type: EventType
    durability_class: DurabilityClass
    session_id: SessionId
    sequence_number: int
    occurred_at: datetime
    payload: Mapping[str, object] = field(default_factory=dict)
    call_id: CallId | None = None
    turn_id: TurnId | None = None
    ownership_epoch: int | None = None
    generation_id: GenerationId | None = None
    operation_id: OperationId | None = None
    worker_id: WorkerId | None = None
    clock_domain: str | None = None
    monotonic_offset_ns: int | None = None

    def __post_init__(self) -> None:
        """Enforce schema, durability, clock, and payload invariants.

        Raises:
            TypeError: If a field has an invalid runtime type.
            ValueError: If a value violates the event contract.

        Solution category:
            Aggregate boundary validation followed by deep payload freezing.

        Complexity:
            O(n) time and space for ``n`` payload values; other checks are O(1).
        """
        # 1. Validate identity and enum types that annotations do not enforce.
        required_types: tuple[tuple[str, object, type[object]], ...] = (
            ("event_id", self.event_id, EventId),
            ("event_type", self.event_type, EventType),
            ("durability_class", self.durability_class, DurabilityClass),
            ("session_id", self.session_id, SessionId),
            ("occurred_at", self.occurred_at, datetime),
        )
        for name, value, expected_type in required_types:
            if not isinstance(value, expected_type):
                raise TypeError(f"{name} must be {expected_type.__name__}")

        optional_types: tuple[tuple[str, object | None, type[object]], ...] = (
            ("call_id", self.call_id, CallId),
            ("turn_id", self.turn_id, TurnId),
            ("generation_id", self.generation_id, GenerationId),
            ("operation_id", self.operation_id, OperationId),
            ("worker_id", self.worker_id, WorkerId),
        )
        for name, value, expected_type in optional_types:
            if value is not None and not isinstance(value, expected_type):
                raise TypeError(f"{name} must be {expected_type.__name__} or None")

        # 2. Validate scalar values and supported schema versions.
        _required_int(self.schema_version, name="schema_version", minimum=1)
        _required_int(self.sequence_number, name="sequence_number", minimum=1)
        if self.schema_version not in SUPPORTED_SCHEMA_VERSIONS:
            raise ValueError(f"unsupported schema_version: {self.schema_version}")
        if self.ownership_epoch is not None:
            _required_int(self.ownership_epoch, name="ownership_epoch", minimum=1)
        if self.monotonic_offset_ns is not None:
            _required_int(
                self.monotonic_offset_ns, name="monotonic_offset_ns", minimum=0
            )

        # 3. Require registry policy rather than trusting each producer.
        expected_durability = EVENT_REGISTRY[self.event_type].durability
        if self.durability_class is not expected_durability:
            raise ValueError(
                f"{self.event_type} requires durability {expected_durability}"
            )

        # 4. Reject ambiguous wall-clock and monotonic-clock metadata.
        if self.occurred_at.tzinfo is None or self.occurred_at.utcoffset() is None:
            raise ValueError("occurred_at must be timezone-aware")
        if (self.clock_domain is None) != (self.monotonic_offset_ns is None):
            raise ValueError(
                "clock_domain and monotonic_offset_ns must be provided together"
            )
        if self.clock_domain is not None and not self.clock_domain.strip():
            raise ValueError("clock_domain must not be blank")

        # 5. Replace caller-owned containers with an immutable validated copy.
        frozen_payload = _freeze_json(self.payload)
        if not isinstance(frozen_payload, Mapping):
            raise TypeError("payload must be a JSON object")
        object.__setattr__(self, "payload", frozen_payload)

    @classmethod
    def create(
        cls,
        *,
        event_type: EventType,
        session_id: SessionId,
        sequence_number: int,
        payload: Mapping[str, object] | None = None,
        call_id: CallId | None = None,
        turn_id: TurnId | None = None,
        ownership_epoch: int | None = None,
        generation_id: GenerationId | None = None,
        operation_id: OperationId | None = None,
        worker_id: WorkerId | None = None,
        clock_domain: str | None = None,
        monotonic_offset_ns: int | None = None,
        occurred_at: datetime | None = None,
    ) -> Self:
        """Create a current-schema event using registry-owned durability.

        Solution category:
            Factory method centralizing generated/default metadata and policy.

        Complexity:
            O(n) time and space for ``n`` payload values due to defensive
            freezing; UUID and scalar metadata work is O(1).
        """
        # 1. Derive policy fields instead of asking producers to duplicate them.
        if not isinstance(event_type, EventType):
            raise TypeError("event_type must be EventType")
        durability = EVENT_REGISTRY[event_type].durability

        # 2. Construct through the same invariant checks as deserialized events.
        return cls(
            event_id=EventId.new(),
            schema_version=CURRENT_SCHEMA_VERSION,
            event_type=event_type,
            durability_class=durability,
            session_id=session_id,
            sequence_number=sequence_number,
            occurred_at=occurred_at or datetime.now(UTC),
            payload={} if payload is None else payload,
            call_id=call_id,
            turn_id=turn_id,
            ownership_epoch=ownership_epoch,
            generation_id=generation_id,
            operation_id=operation_id,
            worker_id=worker_id,
            clock_domain=clock_domain,
            monotonic_offset_ns=monotonic_offset_ns,
        )

    def to_dict(self) -> dict[str, object]:
        """Return the versioned wire representation as detached Python values.

        Solution category:
            Explicit schema projection rather than reflection-based serialization.

        Complexity:
            O(n) time and space for ``n`` payload values copied into mutable JSON
            containers; scalar metadata work is O(1).
        """
        # 1. Emit every schema field explicitly so changes require code review.
        return {
            "event_id": str(self.event_id),
            "schema_version": self.schema_version,
            "event_type": self.event_type.value,
            "durability_class": self.durability_class.value,
            "session_id": str(self.session_id),
            "call_id": str(self.call_id) if self.call_id else None,
            "turn_id": str(self.turn_id) if self.turn_id else None,
            "ownership_epoch": self.ownership_epoch,
            "generation_id": str(self.generation_id) if self.generation_id else None,
            "operation_id": str(self.operation_id) if self.operation_id else None,
            "worker_id": str(self.worker_id) if self.worker_id else None,
            "sequence_number": self.sequence_number,
            "occurred_at": self.occurred_at.astimezone(UTC)
            .isoformat(timespec="microseconds")
            .replace("+00:00", "Z"),
            "clock_domain": self.clock_domain,
            "monotonic_offset_ns": self.monotonic_offset_ns,
            "payload": _thaw_json(self.payload),
        }

    def to_json(self) -> str:
        """Serialize this event into deterministic compact JSON text.

        Solution category:
            Canonical serialization with sorted keys and fixed separators.

        Complexity:
            O(n log k) worst-case sorting work across JSON objects, where ``n``
            is serialized data size and ``k`` is object key count; O(n) output
            space. Python's encoder implementation determines exact constants.
        """
        return json.dumps(
            self.to_dict(),
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )

    @classmethod
    def from_json(cls, serialized: str) -> Self:
        """Deserialize untrusted JSON text through the full envelope contract.

        Raises:
            TypeError: If the document or a field has the wrong JSON type.
            ValueError: If JSON, identity, enum, timestamp, or invariant data is
                invalid, duplicated, missing, unsupported, or unknown.

        Solution category:
            Strict boundary parsing followed by aggregate validation.

        Complexity:
            O(n) parse/validation time plus object-key sorting performed only by
            later serialization, and O(n + d) space for input size ``n`` and
            nesting depth ``d``.
        """
        # 1. Parse JSON while rejecting duplicate keys and non-standard numbers.
        decoded = json.loads(
            serialized,
            object_pairs_hook=_parse_json_object,
            parse_constant=_reject_json_constant,
        )
        if not isinstance(decoded, dict):
            raise TypeError("event envelope must be a JSON object")

        # 2. Reject schema drift rather than silently ignoring unknown fields.
        fields = frozenset(decoded)
        if fields != _SERIALIZED_FIELDS:
            missing = sorted(_SERIALIZED_FIELDS - fields)
            unknown = sorted(fields - _SERIALIZED_FIELDS)
            raise ValueError(
                f"invalid envelope fields; missing={missing}, unknown={unknown}"
            )

        # 3. Parse boundary primitives into strong internal values.
        event_id_raw = decoded["event_id"]
        session_id_raw = decoded["session_id"]
        occurred_at_raw = decoded["occurred_at"]
        payload_raw = decoded["payload"]
        if not isinstance(event_id_raw, str):
            raise TypeError("event_id must be text")
        if not isinstance(session_id_raw, str):
            raise TypeError("session_id must be text")
        if not isinstance(occurred_at_raw, str):
            raise TypeError("occurred_at must be text")
        if not isinstance(payload_raw, dict):
            raise TypeError("payload must be a JSON object")

        clock_domain_raw = decoded["clock_domain"]
        if clock_domain_raw is not None and not isinstance(clock_domain_raw, str):
            raise TypeError("clock_domain must be text or null")

        # 4. Construct the envelope so all cross-field invariants run once.
        return cls(
            event_id=EventId.parse(event_id_raw),
            schema_version=_required_int(
                decoded["schema_version"], name="schema_version", minimum=1
            ),
            event_type=EventType(decoded["event_type"]),
            durability_class=DurabilityClass(decoded["durability_class"]),
            session_id=SessionId.parse(session_id_raw),
            call_id=_optional_identifier(decoded["call_id"], CallId),
            turn_id=_optional_identifier(decoded["turn_id"], TurnId),
            ownership_epoch=(
                None
                if decoded["ownership_epoch"] is None
                else _required_int(
                    decoded["ownership_epoch"], name="ownership_epoch", minimum=1
                )
            ),
            generation_id=_optional_identifier(decoded["generation_id"], GenerationId),
            operation_id=_optional_identifier(decoded["operation_id"], OperationId),
            worker_id=_optional_identifier(decoded["worker_id"], WorkerId),
            sequence_number=_required_int(
                decoded["sequence_number"], name="sequence_number", minimum=1
            ),
            occurred_at=datetime.fromisoformat(occurred_at_raw.replace("Z", "+00:00")),
            clock_domain=clock_domain_raw,
            monotonic_offset_ns=(
                None
                if decoded["monotonic_offset_ns"] is None
                else _required_int(
                    decoded["monotonic_offset_ns"],
                    name="monotonic_offset_ns",
                    minimum=0,
                )
            ),
            payload=payload_raw,
        )
