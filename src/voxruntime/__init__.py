"""Public package boundary for VoxRuntime.

Importing this package intentionally performs no network, filesystem, database,
thread, or asynchronous-task setup. Application startup belongs in an explicit
entry point so imports remain safe and deterministic.
"""

from voxruntime.domain.identifiers import SessionId

__all__ = ["SessionId"]
