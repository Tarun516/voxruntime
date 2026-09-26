# Learning Path: From First Program to Independent Engineering

## How to Use This Path

You do not need to finish a textbook before starting VoxRuntime. Learn the
prerequisites for the next small checkpoint, use them, inspect what happened,
then return to the concept at greater depth. The phases below are a curriculum;
the design document remains the authority for product requirements.

Begin with [the foundations handbook](foundations.md). It supplies initial
explanations, examples, and questions. Each implementation checkpoint expands
the relevant concepts with real source code and experiments. The handbook is
a growing reference, not a claim to cover all computer science.

## Learning Tracks and Observable Outcomes

| Track | First encounter | Deeper project work | Evidence of independent use |
|---|---|---|---|
| Computer execution | Before 0.1: files, shell, interpreter, process | Frames, objects, tasks, sockets, cleanup | Trace a new program from command to output |
| Python | 0.1: names, values, functions, modules | Types, exceptions, protocols, async, testing | Implement a small variation and explain its behavior |
| Algorithms/data structures | Phase 0: containers, lookup, state transitions | Queues, buffering, deduplication, routing | Choose a structure from workload and explain cost |
| Backend systems | Phase 0 interfaces; Phase 4 HTTP/storage | Transactions, schemas, auth, APIs | Design and test an unfamiliar request path |
| Concurrency/distribution | Phase 0 tasks/cancellation | Recovery, ownership, partitions, fencing | Explain a failure timeline and enforce an invariant |
| Audio/voice | Phase 1 samples/frames/streaming | Endpointing, interruption, codecs, transport | Diagnose where speech latency or corruption occurs |
| AI fundamentals | Before the first model adapter | Tokenization, inference, tools, context, evaluation | Separate model behavior from application guarantees |
| Performance | 0.1 measurement basics | Allocation, event-loop lag, saturation | Profile first, change one factor, verify trade-offs |
| Operations/security | Local configuration and secret handling | Isolation, deployment, retention, restore | Diagnose an incident using observable evidence |
| Independent learning | Every checkpoint | Version changes, unfamiliar libraries | Read a contract, form a hypothesis, test and revise |

## Before Checkpoint 0.1

Learn what a terminal command is, how a working directory affects file lookup,
what source code contains, what Python executes, and how a function receives and
returns values. Run a tiny example, deliberately cause an error, and read the
error from its final message back to the relevant source location.

Learn how project files differ: source tells the program what to do;
configuration tells tools how to behave; tests exercise expectations;
documentation records reasoning. A virtual environment isolates installed
Python packages; it is not a separate machine.

Prerequisite practice is part of 0.1 preparation, not an extra production phase.
No prior fluency is assumed.

## Phase 0: Explain the Program Before Connecting Services

Follow the canonical checkpoints 0.1-0.8 in the design document. The finer
lesson sequence in the implementation roadmap subdivides them; it does not
renumber the canonical checkpoints.

| Canonical checkpoint | Teaching slices |
|---|---|
| 0.1 Repository/domain skeleton | Execution, packaging, names, identity values, import boundaries |
| 0.2 Canonical events | Objects, schemas, serialization, immutable data, identity |
| 0.3 Orthogonal states | Conditions, enums, transition tables, independent activities |
| 0.4 Identity/causality | Stale results, ordering, equality, generation checks |
| 0.5 Cancellation | Coroutines, tasks, suspension, exceptions, cleanup |
| 0.6 Providers/fakes | Interfaces, substitution, streaming, deterministic testing |
| 0.7 Tool operations | Side effects, logical action versus attempt, uncertainty |
| 0.8 Clocks/latency | Units, monotonic time, measurement boundaries, overlap |

An integrated simulation and race suite consolidate these lessons. Phase 0
models distributed contracts; it does not claim to implement durable database
fencing or crash recovery before Phase 4.

## Phases 1-2: Follow Real Audio

Learn sampling and bytes before frame formats. Learn producers and consumers
before streaming adapters. Trace a single frame through transport, conversion,
queue, and consumer. Then trace a complete conversation turn.

Measure delays at defined boundaries. Interrupt output and inspect which tasks
stop, which buffers empty, and which late results are rejected. Explain why
speech recognition, deciding the turn is finished, and deciding what to say
are separate responsibilities.

## Phases 3-4: Connect Words to Business State

Build a small domain example before exposing it as an AI tool. Learn validation,
authorization, SQL tables, unique constraints, and transactions through an
appointment operation. Simulate a lost response and reason about whether the
appointment exists. Explain why retrying a request is a business correctness
decision.

## Phases 5-6: Add Distance and Multiple Owners

Learn transport and coordination failures by drawing timelines. Distinguish a
dead process from a process that is merely unreachable. Observe how a lease
can expire while an old process is still running. Follow authority from durable
storage to the point that admits a protected mutation or media publisher.

## Phases 7-9: Operate and Evaluate

Build explanations from logs, metrics, traces, test fixtures, and actual business
state. Learn distributions, percentiles, baselines, and controlled experiments.
Practise forming several possible causes of a symptom before changing code.

## Phase 10 and the Bridge to Core AI

Before implementing local inference, introduce the mathematical prerequisites:
vectors and matrices as collections and transformations of numbers;
probability as uncertainty; derivatives as rates of change; gradients as
directions for changing many parameters; and optimization as repeated updates
toward an objective.

Connect these to token embeddings, attention, model parameters, loss functions,
training, inference, batching, and GPU memory. Each topic needs its own worked
numerical example and exercise when reached. These lessons are planned, not
already taught by the short AI introduction in the handbook.

Using a hosted model does not demonstrate understanding of its training
algorithm. Track systems understanding and model/mathematics understanding
separately.

## Transfer Beyond This Project

At each checkpoint, apply a principle to another domain: bounded queues to file
uploads, idempotency to order placement, state machines to downloads, evaluation
to a classifier, or cancellation to a search interface.

To investigate another Python version or an unfamiliar framework:

1. Identify the behavior your code relies on.
2. Locate its documented contract and version changes.
3. Construct the smallest example that exercises it.
4. Predict the result and run it in an isolated environment.
5. Compare results against the prediction and explain discrepancies.
6. Add a compatibility test and document the decision.

The target is the ability to perform this investigation, with progressively less
guidance. Record evidence in [the journal](learning-journal.md).
