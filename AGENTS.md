# VoxRuntime Repository Instructions

## Project Purpose

VoxRuntime is a learning-first implementation of a production-oriented,
multi-tenant realtime voice-agent runtime. Correctness, observability, and a
clear explanation of the system are deliverables alongside working code.

The canonical requirements are in
`VoxRuntime_Production_Engineering_Design_v1.4.docx`. Sections 3-22 and
Appendices A-C are canonical. Sections 26 and 27 preserve design-review history.

## Required Working Method

### Teaching Contract: Assume No Prior Knowledge

The user's primary goal is to become an independent engineer through this
project. Assume unfamiliarity with Python, backend systems, operating systems,
audio, and AI until the learner demonstrates familiarity. Explain respectfully;
do not confuse unfamiliarity with inability. Do not assume that reading a
definition means the concept has been understood.

- Start with the concrete problem, then derive the mechanism and name it.
- Expand acronyms at first use and link prerequisite concepts. Avoid defining
  unfamiliar terms using other unexplained terms.
- Explain all introduced functions, including small helpers and tests. Simple
  functions may have brief explanations; none should be an unexplained box.
- Cover every new syntax form and meaningful statement in checkpoint notes.
  Repeated syntax may link to an earlier explanation. Keep coverage traceable
  by file and symbol; use line numbers only as supplementary references.
- Explain every command, flag, configuration field, dependency, and generated
  artifact that the learner must use: purpose, effects, expected output, and
  common failure. Installation alone does not teach packaging.
- Explain library boundaries: what our code does, what the library supplies,
  what the OS or external service supplies, and what remains unverified.
- Include a prediction exercise, guided experiment, independent variation,
  and a worked explanation. Separate exercise prompts from answers.
- Never mark learner understanding as verified because code/tests passed or
  because the assistant wrote an explanation. Track implementation and learning
  separately; unknown understanding is `not assessed`.
- Provide small reviewable lessons. Do not silently advance across checkpoints.
  Complete the authorized checkpoint; invite reflection without creating a
  mandatory quiz or requiring approval for every routine edit.
- Explain transferable principles and an exercise outside voice AI. Help the
  learner form hypotheses, consult documentation, run experiments, and revise
  conclusions independently.

Read [the teaching method](docs/learning-method.md) and the relevant checkpoint
before implementation. Use [the foundations handbook](docs/foundations.md),
[learning path](docs/learning-path.md), and
[learning journal](docs/learning-journal.md) as living teaching resources.

For every function, record its solution category (for example validation,
transformation, state transition, orchestration, or I/O adapter), algorithm or
pattern where applicable, time/space costs, and why the approach fits. A trivial
function may use one sentence. Say `not applicable` with a reason rather than
inventing an algorithm. Resource measurements belong to meaningful workloads;
do not fabricate precise CPU or byte costs for individual statements.

Implement one checkpoint at a time. Before writing checkpoint code:

1. State the problem and the failure that motivates the work.
2. Identify the invariant or contract the implementation must preserve.
3. Describe control flow, data flow, and ownership boundaries.
4. Identify Python/runtime behavior that materially affects the design.
5. Define tests and observable exit evidence.

After implementation:

1. Run the smallest relevant verification first, then the broader suite.
2. Record failure-path and race-condition coverage where applicable.
3. Update the checkpoint learning note and resource model.
4. Record meaningful architectural choices in an ADR.
5. Do not claim performance, capacity, or memory properties without evidence.

## Code Documentation Standard

Public modules, classes, functions, and methods require docstrings. A
non-trivial private function also requires a docstring when its purpose,
invariant, side effects, or constraints are not obvious.

Function documentation should explain, when applicable:

- what the function guarantees and why it exists;
- arguments, returned value, side effects, and ownership changes;
- exceptions, cancellation behavior, and important restrictions;
- time and auxiliary-space complexity;
- I/O, allocation, or scheduling behavior not represented by Big-O notation.

Use numbered comments inside non-trivial functions to label meaningful phases:

```python
def example() -> None:
    """Perform an example operation and preserve its invariant."""

    # 1. Validate the boundary input before changing state.
    ...

    # 2. Commit the state transition atomically.
    ...
```

Do not number every statement or comment on obvious syntax. Comments explain
intent, constraints, ordering, and surprising behavior. Code and comments must
be changed together.

## Complexity and Resource Notes

For every non-trivial function or solution, document complexity using named
input variables, for example `n = number of events`. Do not write `O(n)` without
identifying `n`.

Separate these concerns:

- algorithmic time and auxiliary space;
- persistent or retained memory;
- Python object allocation/copying;
- CPU-bound work;
- event-loop scheduling or lock contention;
- network, database, filesystem, and provider latency;
- measured behavior versus theoretical behavior.

An operation being `O(1)` does not imply that it is fast when it performs I/O.
Measure hot paths and capacity-sensitive behavior.

## Python and Async Rules

- Use Python 3.12+ and explicit type annotations.
- Keep domain/runtime logic independent of vendor SDKs.
- Use monotonic clocks for durations; wall clocks are for correlation/audit.
- Never perform blocking I/O or CPU-heavy work on the asyncio event-loop thread.
- Make queues bounded and document their pressure policy.
- Treat cancellation as cooperative. Cancelling a coroutine does not undo an
  external side effect.
- Use structured concurrency for per-session child tasks.
- Preserve turn, output-generation, operation, and ownership identities across
  asynchronous boundaries.
- Reject or ignore stale results at the authoritative mutation boundary.
- Prefer immutable value objects for identities, events, and configuration.
- Avoid shared mutable global state.

Whenever a language feature affects a design, add a `Python/runtime note` to
the checkpoint document explaining the behavior and chosen approach.

## Realtime and Distributed Correctness

The following invariants are non-negotiable:

- Only the current durable ownership epoch may perform protected operations.
- Authority is validated atomically with the protected mutation.
- At most one publication generation may emit agent audio for a call.
- Stale turn or output generations cannot mutate current state or play audio.
- Side-effecting tools establish recoverable intent before network dispatch.
- An ambiguous external result is `UNKNOWN`, not automatically `FAILED`.
- Generated speech and confirmed/estimated delivery evidence remain distinct.
- Every realtime queue is bounded.
- Correctness-critical events cannot be silently dropped.
- A live call does not depend on control-plane requests on its per-frame path.

## Testing Requirements

Each checkpoint should include, as applicable:

- unit tests for pure rules and state transitions;
- contract tests for adapters and schemas;
- failure tests demonstrating the motivating failure;
- invalid-transition and boundary tests;
- cancellation and task-cleanup tests;
- deterministic concurrency/race tests;
- resource-bound tests for queues and retained state;
- integration tests only after underlying contracts are stable.

Tests assert observable behavior and invariants rather than private
implementation details. A bug fix requires a failing regression test whenever
practical.

## Documentation Layout

- `docs/architecture/`: canonical explanatory architecture.
- `docs/checkpoints/`: one learning record per checkpoint.
- `docs/adr/`: architectural decision records.
- `docs/learning-method.md`: implementation and teaching protocol.
- `docs/glossary.md`: precise shared vocabulary.
- `docs/resource-model.md`: evolving process/task/data/memory/CPU model.

Keep documentation close to the code it explains. Update affected documents in
the same change as behavior or contract changes.

## Scope Discipline

- Build the smallest production-shaped implementation for the active
  checkpoint.
- Do not implement future roadmap features early.
- Do not introduce infrastructure merely because it may be useful later.
- Use deterministic fakes before real external providers.
- Keep assumptions and provisional targets explicitly labeled.
- Do not silently weaken an invariant to make a test pass.

## Change Safety

- Preserve user-authored or unrelated working-tree changes.
- Do not perform destructive Git or filesystem operations without explicit
  authorization.
- Never log credentials, raw secrets, or unnecessary sensitive content.
- Explain migrations, compatibility impact, and rollback for persistent schema
  or public contract changes.
