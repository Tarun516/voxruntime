# Learning-First Engineering Method

## Purpose

This project must produce understanding as well as software. A checkpoint is
not complete merely because its tests pass. It must also explain why the
component exists, how it executes, which failures it prevents, and what it
costs in time and resources.

## How We Approach Implementation Together

The learner should be able to reconstruct the reasoning behind the software.
Assume no background knowledge until established through conversation or an
exercise. Teach one small chain of connected ideas at a time. A definition is
the beginning of an explanation, not evidence of mastery.

Each lesson opens with four sentences: where we are in the system, the user
behavior we need, what currently goes wrong, and what this lesson will enable.
Before introducing an abstraction, show a concrete input, the simplest attempt,
and the limitation that motivates the abstraction.

### Before Writing Code

1. Draw the relevant part of the system and show the entry/exit points.
2. List prerequisite concepts and link their handbook explanations. Teach any
   missing prerequisite in a short worked example before using it.
3. State expected input/output with a realistic value, including units.
4. Ask the learner to predict one behavior; provide an experiment they can run
   independently. Do not make their response a permission gate for routine work.
5. Describe the simplest approach, the failure it permits, and the proposed fix.
6. Explain why each planned file, function, dependency, and type is necessary.

### While Writing Code

Work in slices that introduce one principal idea and can be run or tested.
For each slice, explain syntax, meaning, runtime behavior, and project purpose.
Show the caller and the result consumer so a helper is never taught in isolation.
Explain imports, decorators, annotations, punctuation, and configuration syntax
the first time they appear. Later uses can link to that explanation.

Numbered function comments describe meaningful stages. In Python these use
`# 1.`; `//` means floor division, not a comment. Function docstrings live just
inside the function and explain its contract. Long tutorials belong in the
checkpoint note. Keep both the source documentation and tutorial synchronized.

Keep a walkthrough coverage table: file/symbol, purpose, explanation link,
tests, and resource notes. Cover helpers, test fixtures, entry points, build
configuration, and dependency declarations as well as production functions.
Every line must be explainable; repeated boilerplate can share an explanation.

### After Each Slice

Trace one concrete input through calls, objects, state changes, returns, and
cleanup. For asynchronous work, record task ownership and suspension points.
Explain what changes if the input is empty, invalid, duplicated, delayed, or
cancelled. Select relevant cases and explain why irrelevant ones are excluded.

Provide the exact run command, explain its flags and working directory, and
show expected output separately from output actually observed. A test is evidence
for the behavior exercised, not a proof of every possible schedule or input.

### Build Independence Gradually

Use the sequence: worked example -> guided modification -> independent variant
-> unfamiliar problem. Offer hints before a separate worked solution. Include
one debugging exercise with an observable symptom and one transfer question:
where else would this mechanism be useful, and where would it be unnecessary?

Record implementation status separately from learner progress in the
[journal](learning-journal.md). Do not infer confidence or mastery from silence.
Revisit earlier concepts when they reappear in a harder context.

### Explain Choices Without Turning Them into Universal Rules

For each design decision, state the workload, correctness constraints, simpler
alternative, chosen approach, disadvantage, and evidence that would change it.
Distinguish a Python language guarantee, CPython implementation detail,
version-specific behavior, library guarantee, and our application policy.

For example, a type annotation can help a checker find mistakes, but validating
untrusted input still requires runtime code. An asynchronous API may allow other
work during a wait; it does not make CPU-heavy computation free. Explain these
distinctions when the relevant code is introduced.

### Sources and Uncertainty

Use official language/library documentation for version-sensitive behavior and
record the selected version and relevant link in the lesson. Distinguish observed
output, derived estimates, assumptions, and unresolved questions. Explain how to
read a documentation page: signature, parameters, return value, errors,
guarantees, version changes, and a minimal experiment to test understanding.

### Learning Completion Evidence

A checkpoint has two independent outcomes: engineering evidence and learning
evidence. Engineering completion requires relevant tests and documentation.
Learning evidence may be the learner explaining the flow, predicting output,
fixing a small fault, or applying the idea elsewhere. Record only evidence
actually provided. Optional exercises can remain pending after code is complete.

## Checkpoint Engineering Cycle

Every checkpoint follows this sequence.

### 1. Intuition

Describe the concrete system problem in plain language. Introduce only the
vocabulary required for the checkpoint.

### 2. Failure First

Show what fails without the proposed mechanism. Prefer an executable failing
test or a small reproducible program. If that is not practical, provide a
precise event timeline.

### 3. Contract and Invariant

State what must always remain true. Identify the authoritative component and
the boundary at which the invariant is enforced.

### 4. Design

Explain inputs and outputs, control and data flow, state transitions, ownership
and lifetime, failures, cancellation, concurrency boundaries, and rejected
alternatives.

### 5. Language and Runtime Model

Explain relevant Python behavior, including object/reference semantics,
coroutine suspension, task scheduling, cancellation, garbage collection,
serialization, copying, or native-library boundaries.

### 6. Implement in Small Slices

Prefer the smallest production-shaped implementation that exposes the real
contract. Avoid placeholder abstractions that conceal the concept being
learned.

### 7. Test

Cover the happy path, motivating failure, invalid boundaries, and relevant race
or cancellation cases. Tests should explain the invariant through their names
and assertions.

### 8. Observe

Capture evidence appropriate to the checkpoint:

- execution trace or ordered event list;
- elapsed and CPU time;
- allocation or retained-memory snapshots;
- queue occupancy and event-loop lag;
- task, thread, process, and file-descriptor counts;
- network/database calls and serialized payload size.

### 9. Break It Deliberately

Inject timeout, cancellation, duplicate input, stale identity, queue pressure,
provider failure, or process interruption as relevant.

### 10. Explain and Record

Complete the checkpoint note, update the resource model, and add an ADR when a
choice affects later work.

## Code Walkthrough Standard

For each new module, the learning note explains:

1. Why the module boundary exists.
2. What imports it and what it may import.
3. Each public type and function.
4. Important statements whose ordering or semantics affect correctness.
5. The end-to-end call path through the module.
6. Errors, cancellation, and cleanup.
7. CPU, memory, and I/O implications.

Line-by-line explanation belongs primarily in the checkpoint note. Source code
contains durable documentation: docstrings, type annotations, invariant
comments, and numbered comments for meaningful stages. Repeating self-evident
syntax in comments makes code harder to maintain and is avoided.

## Function Analysis Template

For a non-trivial function, record:

```text
Purpose:
Why needed:
Inputs and ownership:
Output and ownership:
Side effects:
Failure modes:
Cancellation behavior:
Invariant enforced:
Time complexity:
Auxiliary-space complexity:
Retained-memory effect:
I/O and scheduling:
Why this approach:
Alternatives rejected:
```

Complexity variables must be named. For example, `O(n)` becomes “`O(n)`, where
`n` is the number of events in the batch.”

## Theoretical Versus Measured Performance

Theoretical analysis answers how resource use grows with input size. It does
not answer how long remote I/O takes or how much overhead Python objects add.
Every performance-sensitive decision therefore has two records:

- predicted behavior from algorithms and runtime mechanics;
- measured behavior from a reproducible workload.

Measurements include environment, input distribution, warm/cold state, sample
size, and clock boundary. Optimizations require a profile or benchmark showing
the problem and evidence that the change improves it without breaking
correctness.

## Review Questions

- Can the learner explain the motivating failure without looking at the code?
- Is the authoritative owner of each state transition clear?
- Can stale, duplicate, delayed, or cancelled work violate the invariant?
- Is every queue or retained collection bounded or deliberately durable?
- Is cleanup observable and tested?
- Are complexity variables and resource lifetimes identified?
- Are Python-specific decisions explained?
- Can the checkpoint be run and inspected independently?
