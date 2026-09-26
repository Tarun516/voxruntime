# ADR-0001: Python Project and Verification Toolchain

- Status: Accepted
- Date: 2026-09-26
- Deciders: VoxRuntime maintainers
- Related checkpoint: 0.1

## Context

The project needs reproducible installation, formatting, linting, static type
checking, and tests. The learner must be able to see which tool owns each job.
Checkpoint 0.1 has no need for application runtime dependencies.

The execution environment already provides Python 3.12.13 and `uv`. Tool
versions selected by the first lock are recorded in `uv.lock`.

## Decision Drivers

- Support the design document's Python 3.12+ direction.
- Keep dependency resolution and commands explicit and repeatable.
- Use focused tools whose diagnostics are easy to inspect.
- Avoid adding production dependencies before a runtime requirement exists.
- Permit Python 3.12 through 3.14 while checking against the 3.12 language
  baseline.

## Considered Options

1. `uv`, Ruff, mypy, and pytest.
2. Standard-library `venv`/`pip`, Black/Flake8, mypy, and unittest.
3. Poetry with its environment and packaging workflow.

## Decision

Use `uv` for Python selection, dependency resolution, locking, environments,
and package execution. Use `uv_build` as the build backend, Ruff for formatting
and linting, mypy in strict mode for static type checking, and pytest for tests.
Pin the local interpreter through `.python-version` to Python 3.12.

`make check` is the single convenience command. The Makefile only groups the
four visible commands; it does not contain project logic.

## Why This Option

The selected tools provide short commands, one lockfile, fast local feedback,
and strong support for a typed `src` layout. Pytest makes small executable
examples readable. Ruff consolidates two mechanical jobs. Mypy demonstrates
the difference between static analysis and runtime validation.

The standard-library option has fewer tool dependencies but requires more
separate configuration and gives a less direct introduction to the ecosystem
chosen for later phases. Poetry would add a second high-level project model
where `pyproject.toml` and `uv` are sufficient.

## Consequences

### Positive

- `uv.lock` records selected development-tool versions.
- Application imports have no third-party runtime dependency in Checkpoint 0.1.
- Formatting, linting, typing, and behavior have distinct checks.

### Negative

- Contributors must install `uv` and `make` or run the underlying commands.
- Tool configuration and the lockfile are additional concepts to learn.
- Supporting several Python minors requires later CI across those versions.

### Risks and Mitigations

- Broad dependency ranges can select changed tool behavior. The lockfile fixes
  the actual development environment; deliberate upgrades rerun all checks.
- A type checker cannot validate untyped runtime input. Domain constructors
  enforce important invariants and tests exercise both layers.

## Python/Runtime Implications

Python 3.12 determines available syntax and standard-library contracts. Running
on a later compatible version does not prove 3.12 compatibility, so mypy and
Ruff target 3.12 and later CI should execute the suite on supported versions.

## Complexity and Resource Implications

These tools run outside the production hot path. Their time and memory costs
affect development and CI rather than live calls. The package currently installs
no third-party application code.

## Validation

`uv sync --python 3.12` creates a clean environment and builds the editable
package. `make check` formats-checks, lints, type-checks, and executes nine tests.

## Revisit Triggers

- A required tool cannot support the selected Python range.
- CI evidence shows a material reproducibility or performance problem.
- The project requires publishing workflows unsupported by `uv_build`.

