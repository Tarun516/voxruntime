"""Strong identities used to prevent accidental domain-value mixing."""

from dataclasses import dataclass
from typing import Self
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class SessionId:
    """Identify one voice session with an immutable UUID value.

    Why:
        A dedicated type communicates that the value identifies a session and
        prevents APIs from accepting an arbitrary string by convention alone.
        The runtime check preserves the class invariant even though Python type
        annotations are not enforced automatically.

    Attributes:
        value: The standard-library UUID stored by this identity.

    Complexity:
        Construction, equality, hashing, and string conversion operate on one
        fixed-width UUID and are O(1) time and O(1) auxiliary space.
    """

    value: UUID

    def __post_init__(self) -> None:
        """Reject direct construction with a value that is not a UUID.

        Solution category:
            Boundary validation. No search or collection algorithm applies.

        Raises:
            TypeError: If ``value`` is not an instance of ``uuid.UUID``.

        Complexity:
            O(1) time and O(1) auxiliary space because this performs one runtime
            type check and retains no additional data.
        """
        # 1. Enforce at runtime what the annotation communicates to type checkers.
        if not isinstance(self.value, UUID):
            raise TypeError("SessionId value must be a UUID")

    @classmethod
    def new(cls) -> Self:
        """Create a session identity using a random version-4 UUID.

        Solution category:
            Identity generation delegated to Python's standard library.

        Complexity:
            O(1) time and O(1) auxiliary space for the fixed-width UUID. The
            standard library obtains randomness from the operating system.
        """
        # 1. Generate the primitive value before wrapping it in the domain type.
        return cls(uuid4())

    @classmethod
    def parse(cls, raw: str) -> Self:
        """Parse a textual UUID into a validated session identity.

        Args:
            raw: Text expected to contain a UUID accepted by ``uuid.UUID``.

        Returns:
            A new immutable ``SessionId`` representing the parsed UUID.

        Raises:
            ValueError: If ``raw`` is not valid UUID text.
            AttributeError: If an untyped caller supplies a non-string value.

        Solution category:
            Boundary parsing and validation delegated to ``uuid.UUID``.

        Complexity:
            O(n) time in the length ``n`` of ``raw`` and O(1) auxiliary space
            for UUID-sized inputs. UUID text length is practically bounded.
        """
        # 1. Parse external text through the standard library's UUID validator.
        value = UUID(raw)

        # 2. Wrap the primitive in the domain-specific type.
        return cls(value)

    def __str__(self) -> str:
        """Return the canonical lowercase, hyphenated UUID representation.

        Solution category:
            Fixed-width representation delegated to ``uuid.UUID``.

        Complexity:
            O(1) time and O(1) auxiliary space because UUID width is fixed.
        """
        return str(self.value)
