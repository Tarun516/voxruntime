"""Executable examples for the SessionId value object's contract."""

from typing import cast
from uuid import UUID

import pytest

from voxruntime.domain.identifiers import SessionId


def test_new_session_id_contains_a_uuid() -> None:
    """A generated identity owns a real UUID value."""
    session_id = SessionId.new()

    assert isinstance(session_id.value, UUID)


def test_parse_round_trips_canonical_text() -> None:
    """Canonical UUID text parses and serializes without changing identity."""
    raw = "12345678-1234-5678-1234-567812345678"

    session_id = SessionId.parse(raw)

    assert str(session_id) == raw


def test_equal_values_are_equal_and_have_equal_hashes() -> None:
    """Value semantics allow safe dictionary and set membership checks."""
    raw = "12345678-1234-5678-1234-567812345678"

    first = SessionId.parse(raw)
    second = SessionId.parse(raw)

    assert first == second
    assert hash(first) == hash(second)


def test_session_id_is_immutable() -> None:
    """Callers cannot replace the UUID after the identity is constructed."""
    session_id = SessionId.new()

    with pytest.raises(AttributeError):
        # This intentional type error proves the runtime rejects mutation too.
        session_id.value = UUID(  # type: ignore[misc]
            "00000000-0000-0000-0000-000000000000"
        )


def test_invalid_uuid_text_is_rejected() -> None:
    """Unparseable boundary text fails before becoming a domain identity."""
    with pytest.raises(ValueError):
        SessionId.parse("not-a-uuid")


def test_direct_construction_enforces_runtime_type() -> None:
    """An untyped caller cannot bypass the UUID invariant."""
    invalid_value = cast(UUID, "not-a-uuid")

    with pytest.raises(TypeError, match="must be a UUID"):
        SessionId(invalid_value)
