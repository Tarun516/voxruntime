"""Single registry describing every canonical event's meaning and durability."""

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Final

from voxruntime.events.types import DurabilityClass, EventType


@dataclass(frozen=True, slots=True)
class EventDefinition:
    """Describe stable policy attached to one event type.

    Complexity:
        Construction and field access are O(1) time and O(1) auxiliary space.
    """

    durability: DurabilityClass
    meaning: str


_MUTABLE_EVENT_REGISTRY: dict[EventType, EventDefinition] = {
    EventType.CALL_CREATED: EventDefinition(
        DurabilityClass.CRITICAL, "Control record created."
    ),
    EventType.CALL_CONNECTING: EventDefinition(
        DurabilityClass.DIAGNOSTIC, "Media/session setup initiated."
    ),
    EventType.CALL_STARTED: EventDefinition(
        DurabilityClass.CRITICAL, "Call is active."
    ),
    EventType.CALL_ENDING: EventDefinition(
        DurabilityClass.DIAGNOSTIC, "Termination initiated."
    ),
    EventType.CALL_ENDED: EventDefinition(
        DurabilityClass.CRITICAL, "Observed normal terminal event."
    ),
    EventType.CALL_FAILED: EventDefinition(
        DurabilityClass.CRITICAL, "Observed abnormal terminal event."
    ),
    EventType.CALL_TERMINATED_UNOBSERVED: EventDefinition(
        DurabilityClass.CRITICAL,
        "Reconciler established terminal state after worker/media loss.",
    ),
    EventType.USER_SPEECH_STARTED: EventDefinition(
        DurabilityClass.DIAGNOSTIC, "Speech detection began."
    ),
    EventType.USER_SPEECH_STOPPED: EventDefinition(
        DurabilityClass.DIAGNOSTIC, "Speech detector observed end of speech."
    ),
    EventType.STT_PARTIAL: EventDefinition(
        DurabilityClass.HIGH_VOLUME, "Interim transcript update."
    ),
    EventType.STT_FINAL: EventDefinition(
        DurabilityClass.DIAGNOSTIC, "Final transcript segment."
    ),
    EventType.STT_ERROR: EventDefinition(
        DurabilityClass.DIAGNOSTIC, "Streaming STT error."
    ),
    EventType.TURN_STARTED: EventDefinition(
        DurabilityClass.DIAGNOSTIC, "Runtime begins a user-turn epoch."
    ),
    EventType.TURN_COMPLETED: EventDefinition(
        DurabilityClass.DIAGNOSTIC, "Turn resolved normally."
    ),
    EventType.TURN_INTERRUPTED: EventDefinition(
        DurabilityClass.DIAGNOSTIC, "Current output/reasoning was superseded."
    ),
    EventType.LLM_STARTED: EventDefinition(
        DurabilityClass.DIAGNOSTIC, "Model request initiated."
    ),
    EventType.LLM_FIRST_TOKEN: EventDefinition(
        DurabilityClass.DIAGNOSTIC, "First meaningful model delta received."
    ),
    EventType.LLM_COMPLETED: EventDefinition(
        DurabilityClass.DIAGNOSTIC, "Generation completed."
    ),
    EventType.LLM_CANCELLED: EventDefinition(
        DurabilityClass.DIAGNOSTIC, "Generation cancelled or superseded."
    ),
    EventType.LLM_ERROR: EventDefinition(
        DurabilityClass.DIAGNOSTIC, "Model call failed."
    ),
    EventType.TOOL_REQUESTED: EventDefinition(
        DurabilityClass.DIAGNOSTIC, "Runtime requested a logical tool operation."
    ),
    EventType.TOOL_VALIDATED: EventDefinition(
        DurabilityClass.DIAGNOSTIC, "Tool validation passed."
    ),
    EventType.TOOL_DISPATCHED: EventDefinition(
        DurabilityClass.CRITICAL, "Durable dispatch boundary crossed."
    ),
    EventType.TOOL_SUCCEEDED: EventDefinition(
        DurabilityClass.CRITICAL, "Authoritative tool success persisted."
    ),
    EventType.TOOL_FAILED: EventDefinition(
        DurabilityClass.CRITICAL, "Definitive tool non-success persisted."
    ),
    EventType.TOOL_UNKNOWN: EventDefinition(
        DurabilityClass.CRITICAL, "Tool may have committed without a known result."
    ),
    EventType.TOOL_RECONCILED: EventDefinition(
        DurabilityClass.CRITICAL, "Ambiguous tool operation was resolved."
    ),
    EventType.TOOL_DEDUPED: EventDefinition(
        DurabilityClass.CRITICAL, "Existing logical operation/result reused."
    ),
    EventType.TTS_STARTED: EventDefinition(
        DurabilityClass.DIAGNOSTIC, "Synthesis began."
    ),
    EventType.TTS_FIRST_AUDIO: EventDefinition(
        DurabilityClass.DIAGNOSTIC, "First synthesized audio became available."
    ),
    EventType.TTS_COMPLETED: EventDefinition(
        DurabilityClass.DIAGNOSTIC, "Synthesis completed."
    ),
    EventType.TTS_CANCELLED: EventDefinition(
        DurabilityClass.DIAGNOSTIC, "Synthesis cancelled or superseded."
    ),
    EventType.TTS_ERROR: EventDefinition(
        DurabilityClass.DIAGNOSTIC, "Synthesis failed."
    ),
    EventType.AUDIO_OUTPUT_ENQUEUED: EventDefinition(
        DurabilityClass.HIGH_VOLUME, "Output chunk entered playback queue."
    ),
    EventType.AUDIO_OUTPUT_SENT: EventDefinition(
        DurabilityClass.HIGH_VOLUME, "Output chunk handed to media transport."
    ),
    EventType.AUDIO_PLAYBACK_STARTED: EventDefinition(
        DurabilityClass.DIAGNOSTIC, "Playback evidence indicates start."
    ),
    EventType.AUDIO_PLAYBACK_PROGRESS: EventDefinition(
        DurabilityClass.HIGH_VOLUME, "Playback evidence advanced."
    ),
    EventType.AUDIO_PLAYBACK_STOPPED: EventDefinition(
        DurabilityClass.DIAGNOSTIC, "Playback stopped or drained."
    ),
    EventType.AUDIO_PLAYBACK_INVALIDATED: EventDefinition(
        DurabilityClass.DIAGNOSTIC, "Output generation was invalidated."
    ),
    EventType.OWNERSHIP_ACQUIRED: EventDefinition(
        DurabilityClass.CRITICAL, "Durable ownership epoch acquired."
    ),
    EventType.OWNERSHIP_RENEWED: EventDefinition(
        DurabilityClass.HIGH_VOLUME, "Fast coordination lease renewed."
    ),
    EventType.STALE_OWNER_FENCED: EventDefinition(
        DurabilityClass.CRITICAL, "Stale ownership epoch rejected."
    ),
    EventType.MEDIA_PUBLICATION_GRANTED: EventDefinition(
        DurabilityClass.CRITICAL, "Media publication generation admitted."
    ),
    EventType.MEDIA_PUBLICATION_REVOKED: EventDefinition(
        DurabilityClass.CRITICAL, "Media publication generation revoked."
    ),
    EventType.PROVIDER_FALLBACK: EventDefinition(
        DurabilityClass.DIAGNOSTIC, "Fallback provider selected."
    ),
    EventType.CIRCUIT_OPEN: EventDefinition(
        DurabilityClass.DIAGNOSTIC, "Provider or integration circuit opened."
    ),
    EventType.QUEUE_PRESSURE: EventDefinition(
        DurabilityClass.HIGH_VOLUME, "Bounded queue exceeded warning threshold."
    ),
    EventType.WORKER_DRAINING: EventDefinition(
        DurabilityClass.DIAGNOSTIC, "Worker stopped accepting sessions."
    ),
    EventType.CRITICAL_EVENT_PERSISTED: EventDefinition(
        DurabilityClass.CRITICAL, "Critical event durably recorded."
    ),
    EventType.CRITICAL_EVENT_RECOVERED: EventDefinition(
        DurabilityClass.CRITICAL, "Critical state reconstructed."
    ),
    EventType.PROVIDER_USAGE_FINALIZED: EventDefinition(
        DurabilityClass.CRITICAL, "Provider usage finalized."
    ),
    EventType.PROVIDER_USAGE_ESTIMATED: EventDefinition(
        DurabilityClass.CRITICAL,
        "Provider usage estimated after incomplete finalization.",
    ),
    EventType.TRANSFER_STARTED: EventDefinition(
        DurabilityClass.CRITICAL, "Human or endpoint transfer initiated."
    ),
    EventType.TRANSFER_COMPLETED: EventDefinition(
        DurabilityClass.CRITICAL, "Transfer completed and AI authority relinquished."
    ),
    EventType.TRANSFER_FAILED: EventDefinition(
        DurabilityClass.CRITICAL, "Transfer failed and fallback policy executed."
    ),
}

EVENT_REGISTRY: Final[Mapping[EventType, EventDefinition]] = MappingProxyType(
    _MUTABLE_EVENT_REGISTRY
)
