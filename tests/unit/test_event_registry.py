"""Contract tests for the single canonical event registry."""

import pytest

from voxruntime.events.registry import EVENT_REGISTRY, EventDefinition
from voxruntime.events.types import DurabilityClass, EventType


def test_registry_defines_every_event_type_once() -> None:
    """The enum and registry cannot silently diverge."""
    assert set(EVENT_REGISTRY) == set(EventType)
    assert len(EVENT_REGISTRY) == 55
    assert all(definition.meaning for definition in EVENT_REGISTRY.values())


@pytest.mark.parametrize(
    ("event_type", "expected"),
    [
        (EventType.TOOL_DISPATCHED, DurabilityClass.CRITICAL),
        (EventType.STT_FINAL, DurabilityClass.DIAGNOSTIC),
        (EventType.STT_PARTIAL, DurabilityClass.HIGH_VOLUME),
    ],
)
def test_registry_represents_each_durability_behavior(
    event_type: EventType, expected: DurabilityClass
) -> None:
    """Representative critical, diagnostic, and high-volume policies are fixed."""
    assert EVENT_REGISTRY[event_type].durability is expected


def test_registry_is_read_only() -> None:
    """A producer cannot alter global durability policy at runtime."""
    with pytest.raises(TypeError):
        EVENT_REGISTRY[EventType.STT_PARTIAL] = EventDefinition(  # type: ignore[index]
            DurabilityClass.CRITICAL,
            "Unsafe local policy mutation.",
        )
