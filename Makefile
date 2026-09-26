.PHONY: benchmark-events check format inspect

# Keep uv's writable cache inside the checkout for restricted environments.
export UV_CACHE_DIR := .uv-cache

# Run every local quality gate; make stops at the first failing command.
check:
	uv run ruff format --check .
	uv run ruff check .
	uv run mypy
	uv run pytest

# Rewrite Python files into the project's canonical format.
format:
	uv run ruff format .
	uv run ruff check --fix .

# Measure what changes when the VoxRuntime package is imported.
inspect:
	uv run python tools/inspect_import.py

# Measure event-envelope round trips under a repeatable local workload.
benchmark-events:
	uv run python tools/benchmark_events.py --iterations 10000
