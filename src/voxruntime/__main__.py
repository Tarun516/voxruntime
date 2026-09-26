"""Command-line entry point for the Checkpoint 0.1 executable."""

from voxruntime.domain.identifiers import SessionId


def main() -> int:
    """Create and display a session identity to prove package wiring.

    Why:
        Checkpoint 0.1 needs one observable path from the operating-system
        process entry point into the domain package and back to the shell.

    Returns:
        Process exit status ``0``, which conventionally means success.

    Complexity:
        Time and auxiliary space are O(1) with respect to project input because
        this demonstration creates exactly one identifier. UUID generation
        delegates to Python's standard library and may consult the operating
        system for randomness.
    """
    # 1. Ask the domain type to create a valid new identity.
    session_id = SessionId.new()

    # 2. Cross the output boundary only in the application entry point.
    print(f"VoxRuntime session: {session_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
