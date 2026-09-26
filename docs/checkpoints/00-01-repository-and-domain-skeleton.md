# Checkpoint 0.1: Repository and Domain Skeleton

## Status

`COMPLETE` (engineering evidence recorded 2026-09-26; learner practice remains
`not assessed`)

## Learning Objectives

Preparation assumes no Python fluency. Begin with Foundations sections 1-5 and
16, linked from [the learning path](../learning-path.md). Explain the shell,
working directory, interpreter, names, types, functions, imports, and virtual
environment before using tooling commands. Record understanding as not assessed
until the learner supplies evidence.

Teach the checkpoint in four slices: run and trace a tiny program; demonstrate
values and references; create the minimal package; add and explain verification
tools. For each slice, provide a prediction prompt, command explanation,
expected output, actual evidence, guided change, and separate worked solution.
Cover every new configuration field and dependency in the walkthrough.

After this checkpoint, the learner should be able to explain:

- how a Python process finds and imports a package;
- the difference between a package, module, class, function, and object;
- why dependency direction protects domain logic from vendor SDKs;
- what the test runner imports and executes;
- what type annotations do and do not guarantee at runtime;
- how to inspect process startup time, CPU time, RSS, and Python allocations;
- why a repository skeleton should prove boundaries rather than predict every
  future file.

## Problem

Without an intentional package structure, runtime rules, vendor integrations,
persistence, and application startup quickly become mutually dependent. That
makes individual concepts hard to learn and makes later provider or storage
changes unnecessarily risky.

## Failure Without This Mechanism

A naive implementation might allow a domain state machine to import LiveKit,
FastAPI, or PostgreSQL code directly. Unit tests would then require external
infrastructure, vendor exceptions would leak into core logic, and basic state
rules could not run deterministically.

## Contract and Invariants

- Domain types import no application or adapter modules.
- Provider and persistence boundaries are represented by internal interfaces.
- Vendor SDKs are confined to adapter packages.
- Importing the domain package performs no network, database, or filesystem
  side effects.
- The initial executable demonstrates package wiring without pretending to be
  a realtime call.

## Scope

### Included

- Python project metadata and supported version.
- Source and test package layout.
- Initial domain package and typed identity example.
- Minimal executable entry point proving import and dependency wiring.
- Formatting, linting, type-checking, and test commands.
- A startup/resource inspection example.
- Tests for import safety and the first value-object contract.

### Excluded

- Async session orchestration and state machines.
- Canonical runtime events beyond any minimal bootstrap example.
- LiveKit, STT, LLM, TTS, Redis, PostgreSQL, or FastAPI integrations.
- Containers and deployment manifests.

## Proposed Shape

The exact names will be finalized before implementation, but the intended
dependency direction is:

```text
src/voxruntime/
  domain/       # Pure identities, values, invariants, and policies.
  events/       # Added when the canonical event checkpoint begins.
  runtime/      # Added when runtime contracts begin.
  ports/        # Internal interfaces required by core code.
  adapters/     # Vendor/database/media implementations added later.
  apps/         # Process entry points and composition roots.

tests/
  unit/
  contract/
  integration/
```

Directories are created only when the active checkpoint needs them; the tree
above expresses direction, not an instruction to add empty packages.

## Initial Execution Flow

```text
shell
  -> operating system starts Python
  -> Python initializes the interpreter
  -> module runner resolves the VoxRuntime package
  -> package/module bytecode executes once during import
  -> application entry function constructs explicit dependencies
  -> demonstration command creates a domain value
  -> process returns an exit status to the shell
```

The walkthrough will distinguish module import-time execution from function
invocation and explain why import-time I/O is prohibited.

## Resource Questions to Measure

- Baseline interpreter startup wall and CPU time.
- RSS after importing the empty/minimal package.
- Additional Python allocations caused by importing VoxRuntime.
- Module count before and after the import.
- Whether the entry point creates additional threads or tasks.

These measurements teach inspection technique; they are not production
capacity benchmarks.

## Test Plan

### Happy Path

- Import the top-level package.
- Run the minimal entry point.
- Construct and compare the first immutable identity type.

### Boundaries

- Reject invalid identity input.
- Verify type/value equality and hash behavior where applicable.
- Verify domain modules do not import adapter/vendor packages.

### Side Effects

- Demonstrate that importing the domain package requires no configured network,
  database, secret, or filesystem service.

## Tooling Decision Gate

Before code is added, choose and document the build/project manager, formatter,
linter, static type checker, test runner, supported Python policy, and optional
command runner.

The choice should favor transparent commands and understandable configuration.
An ADR will explain the selected toolchain and rejected alternatives.

## Exit Criteria

- [x] A clean environment can install the project from declared metadata.
- [x] One documented command runs formatting/lint/type/test verification.
- [x] A minimal executable imports and uses the domain package.
- [x] Domain imports have no external side effects detected by the defined tests.
- [x] Dependency-direction checks exist.
- [x] Startup CPU/memory/import observations are recorded.
- [x] Every introduced file and symbol is covered by the walkthrough below.
- [x] Toolchain and package-layout ADRs are accepted.

## Implemented Files and Responsibilities

| File | Responsibility | Why it exists |
|---|---|---|
| `.python-version` | Select Python 3.12 for `uv` | Keeps local work on the minimum supported language version |
| `pyproject.toml` | Package metadata, dependencies, tool configuration, console entry point | Gives build and development tools one declared project contract |
| `uv.lock` | Exact resolved tool packages | Makes the selected environment repeatable |
| `Makefile` | Names `check`, `format`, and `inspect` command groups | Keeps the underlying tool commands visible |
| `.gitignore` | Excludes generated local artifacts | Prevents caches and environments becoming source |
| `src/voxruntime/__init__.py` | Public package boundary | Re-exports the deliberately small public API |
| `src/voxruntime/__main__.py` | Minimal process entry point | Proves OS process -> Python -> application -> domain flow |
| `src/voxruntime/py.typed` | Typed-package marker | Tells compatible checkers that distributed annotations are intentional |
| `src/voxruntime/domain/__init__.py` | Domain package boundary | Exposes pure domain types without infrastructure |
| `src/voxruntime/domain/identifiers.py` | Immutable `SessionId` | Establishes the first domain invariant and value-object example |
| `tests/unit/test_session_id.py` | Identity contract examples | Checks construction, parsing, equality, hashing, and rejection paths |
| `tests/architecture/test_domain_dependencies.py` | Domain dependency rule | Detects forbidden imports by parsing source without executing it |
| `tests/integration/test_package_entrypoint.py` | Fresh-process import and entry point tests | Checks process-visible behavior and absence of added import threads/output |
| `tools/inspect_import.py` | Import resource experiment | Measures import time, traced allocations, modules, threads, and peak RSS |
| `docs/adr/0001-python-toolchain.md` | Toolchain decision | Records options, reasoning, costs, and revisit triggers |
| `docs/adr/0002-source-layout-and-domain-boundary.md` | Package-boundary decision | Records dependency direction and import policy |

No empty `events`, `runtime`, `ports`, or `adapters` packages were created.
Their responsibilities begin in later checkpoints.

## Tool and Configuration Walkthrough

`pyproject.toml` is written in TOML, a configuration format with tables in
square brackets and `key = value` assignments. `[build-system]` tells packaging
tools to use `uv_build`. `[project]` describes the installable package and
declares no runtime dependencies. `[project.scripts]` creates the `voxruntime`
console command and maps it to `voxruntime.__main__:main`, meaning the `main`
object inside that module.

`[dependency-groups].dev` contains tools needed to develop the project rather
than to run its application. Version ranges constrain deliberate upgrades;
`uv.lock` records the exact resolution used now. Ruff targets Python 3.12 and
enforces formatting plus selected correctness/readability rules. Mypy uses
strict mode, which treats missing annotations and several unsafe assumptions as
errors. Pytest discovers tests below `tests/` and rejects unknown configuration
or marker names.

`.python-version` contains `3.12`, so `uv` selects the installed Python 3.12.13
interpreter. The project metadata permits Python 3.12, 3.13, and 3.14; later CI
must actually test the full supported range.

The Makefile declares three *phony* targets, meaning their names represent
actions rather than output files. Each indented recipe runs a command. `make`
stops on the first nonzero exit code. `UV_CACHE_DIR` points to a writable local
cache, which matters in restricted environments and is ignored by Git.

## Source Walkthrough

### Package Initializers

Both `__init__.py` files are executed as package modules during import. They
perform only imports and name binding. `__all__` documents the intentional
public names used by wildcard import and documentation tools. It is an API
signal, not a security boundary.

### `SessionId`

`@dataclass` asks Python to generate initialization, equality, representation,
and related value-object behavior from annotated fields. `frozen=True` makes
ordinary attribute reassignment fail. `slots=True` declares fixed instance
storage and removes the normal per-instance attribute dictionary. These choices
express immutability and reduce accidental state; neither makes every reachable
child object immutable in the general case.

The stored `UUID` is a standard-library object representing 128 bits. A specific
domain type prevents a function signature from treating every identifier as an
undifferentiated string. `__post_init__` runs after the generated initializer
and performs the runtime check that an annotation alone would not perform.

`SessionId.new` is a class method: it receives the class as `cls`, generates a
version-4 UUID through `uuid4`, and returns the same class. `Self` tells the type
checker that a subclass call would return that subclass type. The randomness
source and UUID construction belong to the standard library/operating-system
boundary rather than our own algorithm.

`SessionId.parse` converts external text into the primitive validated value and
then wraps it. Its two numbered steps make the boundary visible. `__str__` uses
Python's special-method protocol so `str(session_id)` and formatted output use
the canonical UUID representation.

All operations on the fixed-width UUID are treated as O(1) for this domain.
Parsing is documented as O(n), where `n` is input text length, while also noting
that accepted UUID text is practically bounded. The object retains one UUID;
it performs no network, filesystem, database, or asynchronous I/O.

### Entry Point

`main` creates one domain value, writes one line to standard output, and returns
integer status 0. `if __name__ == "__main__"` is true when Python executes the
module as the program. `SystemExit(main())` converts the returned status into the
process exit status observed by the shell.

Execution is:

```text
shell -> uv -> Python 3.12 process -> installed console wrapper
      -> voxruntime.__main__.main -> SessionId.new -> uuid.uuid4
      -> print -> standard output -> return 0 -> operating system
```

## Test Walkthrough

Each `test_...` function is discovered and called by pytest. Plain `assert`
expressions become rich failure diagnostics under pytest. `pytest.raises`
checks that invalid input or mutation follows the required exception path.

The immutability test deliberately writes code mypy rejects; the narrow
`# type: ignore[misc]` documents that this single static error is intentional so
the runtime behavior can be tested. `cast` changes what a type checker believes
and does not convert the runtime string, which is why it is useful for testing
an untyped caller crossing the boundary.

The architecture test reads domain source, parses it into an abstract syntax
tree (AST), walks import nodes, and compares their top-level roots with a
forbidden set. For total syntax nodes `n` and distinct imports `i`, this uses
O(n) time and O(i) collected-result space after reading each file. It is a
focused guard, not proof against dynamic imports or conceptual coupling.

The integration tests use `subprocess.run` to create fresh Python processes.
One process imports the package and asserts that it produces no output and does
not increase its thread count from one. The other executes `python -m
voxruntime`, checks status/output, and parses the printed suffix as a UUID.
Copying the process environment costs O(e) time and space for `e` entries.

## Commands and Observed Evidence

Run all commands from the repository root.

```bash
uv sync --python 3.12
```

`sync` resolves `pyproject.toml`, creates `.venv`, builds an editable local
package, installs development tools, and updates the lockfile. `--python 3.12`
selects the required interpreter. Observed: Python 3.12.13, 12 installed
packages including the editable VoxRuntime package.

The project was also built into a source archive and wheel. The wheel was
installed with no dependency cache into a new temporary Python 3.12 virtual
environment, and its installed `voxruntime` command completed successfully.
This checks the packaged artifact rather than relying only on the source tree.

```bash
make check
```

Observed: 21 files already formatted, Ruff passed, mypy reported no issues in
eight source files, and nine pytest tests passed in 0.15 seconds. The timing is
one observation, not a test-duration guarantee.

```bash
UV_CACHE_DIR=.uv-cache uv run voxruntime
```

Observed one line containing `VoxRuntime session:` followed by a random UUID and
status 0. `uv run` executes in the synchronized project environment.

```bash
make inspect
```

One observed run reported Python 3.12.13, 20 additionally imported modules,
one thread both before and after import, about 1,782,372 bytes of positive net
traced Python allocation differences, and roughly 83.5 ms of measured import
wall time while tracing. The process peak RSS was already 36,884 KiB before the
measured import and did not increase. `tracemalloc` and the inspection tool add
substantial overhead, so this is diagnostic evidence rather than normal startup
performance.

Five separate `/usr/bin/time` runs produced:

| Workload | Observed wall time | Observed max RSS range |
|---|---:|---:|
| `.venv/bin/python -c "pass"` | 0.02 s in all five runs | 11,156-11,376 KiB |
| `PYTHONPATH=src .venv/bin/python -c "import voxruntime"` | 0.06-0.07 s | 14,060-14,360 KiB |

The samples suggest about 0.04-0.05 s additional startup time and roughly
2.7-3.2 MiB additional peak RSS for this import graph on this environment.
They do not isolate every source of overhead, establish capacity, or predict a
long-running worker. RSS includes interpreter/native memory; traced allocations
cover Python-traced allocations and can differ from RSS.

## Exercises

### Prompts

1. Before running it, predict whether two `SessionId.parse` calls with the same
   text compare equal and whether they are the same object.
2. Add a temporary print statement at the top level of `identifiers.py`. Run the
   import integration test, explain the failure, then remove the statement.
3. Pass a plain string directly to `SessionId` without `cast`. Compare mypy's
   response with the runtime `__post_init__` response.
4. Create a separate `AppointmentId` with the same representation. Explain why
   static types are more useful than passing one generic UUID everywhere.
5. Transfer the architecture rule to an order-processing system: which package
   should know the payment vendor SDK, and which should own order rules?

### Hints

1. Dataclass equality compares class and field values; Python's `is` asks about
   object identity.
2. The test requires empty standard output during import.
3. Static checking happens before execution only when the checker is run;
   runtime validation happens during construction.
4. Consider what happens if a developer swaps appointment and session values.
5. Keep business rules independent; put vendor translation at an adapter edge.

### Worked Explanations

1. The two values compare equal because both are `SessionId` objects containing
   equal UUIDs. They are separate instances, so `first is second` is false.
2. A top-level print executes during import and violates import safety. Removing
   it restores the quiet package boundary.
3. Mypy reports an incompatible argument. If type checking is bypassed or not
   run, `__post_init__` still raises `TypeError`; the two safeguards operate at
   different times.
4. Two wrapper classes can make swapped identities visible to the checker and
   reader even though both contain UUIDs. Runtime parsing should also preserve
   the intended domain type.
5. Order rules belong in the domain; a payment adapter imports and translates
   the vendor SDK behind an internal interface.

## Learning Status

The implementation and teaching material are complete. Learner prediction,
guided modification, debugging, and independent transfer remain `not assessed`
until the learner performs or explains them. Passing tests is not used as
evidence of learner understanding.

The workspace is now an empty-history Git repository on branch `main`. No
commit was created automatically; checkpoint files remain visible for review
before the first project commit.
