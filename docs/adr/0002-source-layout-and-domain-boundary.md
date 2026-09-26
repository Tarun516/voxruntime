# ADR-0002: Source Layout and Domain Boundary

- Status: Accepted
- Date: 2026-09-26
- Deciders: VoxRuntime maintainers
- Related checkpoint: 0.1

## Context

The design requires domain/runtime rules that can be understood and tested
without LiveKit, databases, web frameworks, or provider SDKs. A careless module
layout can make those infrastructure dependencies available everywhere.

## Decision Drivers

- Make installed-package behavior explicit.
- Keep domain types independent of infrastructure.
- Prevent the repository root from accidentally acting as the package.
- Add directories only when a checkpoint gives them responsibility.
- Provide a clear composition boundary for later applications.

## Considered Options

1. A `src/voxruntime` package with a pure `domain` subpackage.
2. A repository-root `voxruntime` package.
3. Separate installable packages or services for every future component.

## Decision

Use a `src` layout. Start with only the top-level package, the `domain` package,
the command entry point, tests, and diagnostic tools. Add runtime, port, adapter,
and application packages when their checkpoint introduces real code.

Domain code may use the Python standard library and other domain modules. It
must not import application packages, adapters, or vendor libraries. An
architecture test inspects imports without executing domain modules.

## Why This Option

The `src` layout makes tests exercise an installed or explicitly exposed
package rather than succeeding because the current directory happens to contain
a same-named folder. One package keeps early development simple while module
boundaries preserve later extraction options.

Creating separate distributions or services now would add packaging and
network boundaries without a measured scaling, security, or ownership need.

## Consequences

### Positive

- Domain rules run with no infrastructure configuration.
- Imports state their package ownership clearly.
- Empty speculative packages are avoided.

### Negative

- Running directly from source requires installation or `PYTHONPATH=src`.
- Static import rules cannot detect dynamic imports or all architectural
  coupling; review and later tooling remain necessary.

### Risks and Mitigations

- A future edit could import a vendor from the domain package. The architecture
  test rejects known forbidden roots, and review checks conceptual coupling.
- Re-exporting too many internals can create a large public API. `__all__`
  explicitly starts with only `SessionId`.

## Python/Runtime Implications

Importing a module executes top-level statements once per normal interpreter
module cache. Therefore package initializers only bind definitions and exports;
they do not open sockets, read configuration, or create tasks.

## Complexity and Resource Implications

Package lookup and import cost scale with the import graph. The initial measured
import loads 20 additional modules because `dataclasses`, `typing`, and `uuid`
bring standard-library dependencies. No additional thread is created.

## Validation

Unit tests validate `SessionId`; architecture tests inspect domain imports; a
fresh child process verifies that package import stays silent and single-threaded.

## Revisit Triggers

- A component needs independent deployment, security isolation, or scaling.
- Static rules become too weak and require a dedicated dependency checker.
- Public package boundaries need separate release/version lifecycles.

