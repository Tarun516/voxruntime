# Foundations: A First-Principles Companion

## How to Read This

This handbook begins with the machinery underneath a voice agent. Read the
section needed for the current lesson, try its question, and return to it when
the project supplies a real example. No familiarity with Python or backend
systems is assumed.

Each section explains a problem, a mechanism, a project connection, and a common
mistake. The [glossary](glossary.md) provides quick definitions; checkpoint notes
will supply detailed source walkthroughs. New concepts introduced during
implementation must be added here or linked to an equally explicit lesson.

## 1. From a File to a Running Program

A source file is text containing instructions in a programming language.
Stored text does nothing on its own. A processor, or CPU, executes machine
instructions. An operating system manages which programs receive processor
time, memory, and access to devices.

When you run a Python command in a shell, the shell interprets the command and
asks the operating system to launch the Python executable. The resulting
running instance is a process. It has an address space, which is its view of
memory, and handles for resources such as files.

Python is a language; CPython is one implementation of that language. In the
usual CPython execution path, source is parsed, compiled to bytecode, and
executed by the interpreter. Bytecode is an intermediate instruction format;
it is not generally the CPU's native machine code. Native libraries can execute
machine code beneath Python calls.

A module is usually a Python file. Importing it loads its definitions and runs
its top-level statements; later ordinary imports in the same process normally
reuse the cached module. A package groups modules. An entry point is the place
from which an application starts coordinating its work.

In VoxRuntime, understanding startup tells us where configuration is loaded,
where dependencies are constructed, and when sockets or tasks are created.
An import should not unexpectedly start a live call.

**Try:** Draw the path from a shell command to a function printing a value.
Identify which part belongs to the shell, OS, interpreter, and your code.

**Common confusion:** A source file, an installed package, and a running process
are different things. Editing a file does not automatically update every running
process that previously imported it.

## 2. Values, Names, Types, and References

A value is data such as a number or text. A type determines the operations and
behavior available for that value. Python examples include integers, strings,
lists, dictionaries, and user-defined objects.

A variable name refers to an object. Assignment can create another reference
to the same object; it does not necessarily copy the object.

```python
frames = [10, 20]
alias = frames
alias.append(30)
print(frames)
```

Line 1 constructs a list and binds the name `frames` to it. Line 2 binds
`alias` to the same list. Line 3 changes that shared list. Line 4 displays
`[10, 20, 30]`. This is relevant when two pipeline components share a buffer.

A mutable object can change after creation. An immutable object's value cannot
be changed in place. Immutability of an outer object does not automatically
make every referenced child immutable: a tuple can contain a mutable list.

An annotation such as `count: int` communicates an intended type to readers
and checking tools. Python does not generally reject arbitrary assignments just
because an annotation says `int`; input validation must execute actual checks.

**Try:** Predict what changes if line 2 becomes `alias = frames.copy()`.
Then consider a list containing another list: is a shallow copy enough?

**Project connection:** Shared mutable state can allow one task to change data
another task assumes is stable. We choose representations deliberately.

## 3. Functions, Calls, Return Values, and Exceptions

A function groups a named operation. Parameters name its inputs; arguments are
the values supplied during a call. A return value passes a result back to the
caller. A side effect changes something beyond that returned value, such as
writing a file or creating an appointment.

```python
def frame_bytes(samples: int, bytes_per_sample: int) -> int:
    """Calculate the raw payload size for one mono audio frame."""
    # 1. Convert a sample count to a byte count.
    return samples * bytes_per_sample
```

`def` defines a function. Parentheses contain parameters; colons introduce
annotations and the indented body; `-> int` documents the intended return type.
The triple-quoted first statement is the docstring. The multiplication only
executes when called. `frame_bytes(320, 2)` returns 640.

This is an arithmetic transformation, with constant work for the small bounded
integer values assumed here and constant additional space under that assumption.
Python integers can grow arbitrarily large, so arithmetic is not universally
constant-cost when operand bit lengths grow. There is no I/O or special search
algorithm in this example. It assumes valid nonnegative counts; a boundary
accepting untrusted input would need validation.

An exception reports that normal execution cannot continue along the expected
path. A traceback shows the sequence of calls leading to it. Cleanup often
belongs in a `finally` block or a context manager so it runs on error as well
as success.

**Try:** Identify the caller, input units, result units, and invalid inputs.
Explain why this function alone cannot prove an audio buffer is well formed.

## 4. Containers, Algorithms, and Complexity

A data structure organizes values. An algorithm is a procedure for solving a
problem. A list preserves an ordered collection; a dictionary associates keys
with values; a set represents membership; a queue arranges work for consumers.

To find an event in an unsorted list, a linear scan may inspect all `n` events:
time grows as `O(n)`. A hash-based lookup can have average constant lookup work
under its assumptions, but key hashing and collisions still matter. Building
and retaining an index costs memory and update work.

Big-O describes how cost grows as input grows, not a duration in milliseconds.
Auxiliary space is extra working memory beyond the input; retained state may
outlive the function and needs its own accounting. Always define the variables.

**Try:** If ten lookups scan a list of 1,000 events, what work is repeated?
When might building an index be unnecessary?

**Project connection:** We choose structures from access patterns, update rate,
ordering needs, and memory bounds. A named algorithm is not required for every
small helper, but every helper should have an understandable purpose and cost.

## 5. Memory, Lifetimes, and CPU Time

Memory stores active data. Allocating an object consumes memory; retaining a
reference can keep it alive. CPU time measures processor work. Elapsed time
includes waiting, so a network call can be slow while consuming little CPU.

RSS, or resident set size, measures resident process memory, including much
more than application objects. Python allocation measurements do not necessarily
capture all native-library memory. Releasing objects also need not immediately
reduce RSS because allocators may retain memory for reuse.

A leak can mean unintentionally retaining reachable objects forever, not only
forgetting to release manually allocated memory. For example, a session list
that never removes ended sessions can keep transcripts and tasks alive.

**Try:** Describe the lifetime of a frame from receive to playback completion.
Who can still reference it after the producer returns?

**Project connection:** Measure baseline, peak, and post-cleanup memory under a
repeatable workload. Investigate growth across repeated sessions, not just one
snapshot.

## 6. Concurrency, Tasks, and Waiting

Concurrency means managing work whose lifetimes overlap. Parallelism means work
actually executes simultaneously. A process can manage many waiting network
operations without assigning each one its own processor.

A coroutine is a suspendable computation. Calling an `async def` function
creates a coroutine object; it does not by itself finish the work. A task
schedules coroutine execution through an event loop. An event loop coordinates
ready work and I/O notifications.

`await` lets a coroutine obtain the result of an awaitable operation. It can
suspend when that operation is not ready; an already-completed operation may
continue immediately. Therefore, inserting `await` does not guarantee fairness
or a context switch at every occurrence.

A long computation or blocking I/O on the event-loop thread delays other tasks.
Moving it to an appropriate executor or process adds overhead and requires a
clear ownership/cleanup contract.

**Try:** Draw two provider requests overlapping while both wait for network
responses. Mark when the CPU is doing work and when each task is suspended.

**Common confusion:** Async code is not automatically parallel or race-free.
Even one event-loop thread can interleave multi-step operations at suspension
points.

## 7. Queues, Streaming, and Backpressure

A producer creates items; a consumer processes them. A queue temporarily stores
items when those rates differ. Streaming processes a sequence incrementally
instead of waiting for the entire input to exist.

If a producer sends 50 frames per second and a consumer handles 40, the backlog
grows by 10 frames each second while those rates persist. A capacity of 100
frames fills in about 10 seconds from empty. These are simplified assumptions,
not measured platform behavior.

A bounded queue limits item count. To bound bytes, payload size must also be
bounded. Backpressure defines the response to a full queue: wait, reject,
coalesce replaceable updates, or drop data only where policy allows it.

**Try:** Why is dropping a redundant partial transcript different from silently
dropping a final booking result?

**Project connection:** Queues trade buffering tolerance against memory use and
latency. A large buffer can conceal overload while making speech arrive late.

## 8. Backend Requests and Network Boundaries

A backend is the part of an application that processes requests and manages
shared services or data. A client asks for work; a server accepts and responds.
An API is an agreed interface: permitted inputs, outputs, errors, and behavior.

HTTP defines request/response communication, including methods and status
codes. JSON is a text format often used for payloads. Serialization converts
in-memory values into a transferable representation; deserialization reverses
that representation and must be followed by appropriate validation.

A socket is an operating-system interface for communication. Network delivery
introduces delays and failure modes absent from an ordinary local function
call. A timeout means the caller stopped waiting; it does not prove that the
server failed to perform the operation.

Authentication establishes an identity. Authorization decides what that identity
may do. A tenant is a customer or organizational data boundary in a shared
service. Validating a payload does not establish authorization.

**Try:** A booking request times out after the server saves the appointment.
What does the client know, and what remains unknown?

## 9. Databases, Transactions, and Idempotency

A database stores and retrieves structured information. A relational table
organizes rows with defined columns. A schema describes structure and
constraints. An index accelerates selected access patterns at the cost of
storage and write work.

A transaction groups database changes with defined commit/rollback semantics.
Isolation governs what concurrent transactions can observe. Checking a condition
and changing state in separate unprotected steps can permit a race.

Idempotency means repeating an operation has the same intended effect as
performing it once. A stable key can identify repeated requests for one logical
action. A unique key in our database alone cannot prove what happened inside an
external appointment system.

An operation represents the intended action. An attempt represents one network
send. Several attempts can belong to one operation. If the result is ambiguous,
reconciliation obtains evidence, for example by querying an external operation
reference.

**Try:** Explain why generating a fresh idempotency key on every retry defeats
deduplication.

## 10. States, Invariants, and Distributed Ownership

A state records a relevant condition. A state machine defines allowed changes.
An invariant is a property that must hold across those changes, such as “an
ended session cannot become active again.”

Different activities need independent state: listening can overlap synthesis
and playback. One scalar “speaking” flag cannot describe all legal combinations.

In a distributed system, processes communicate over networks and can disagree
about what is alive. A lease expires after a period, but the previous process
may still run. A durable increasing epoch identifies authority; fencing rejects
old authority at the actual mutation boundary.

**Try:** Worker A loses coordination access but still reaches the media server.
Why would starting worker B immediately risk two voices?

**Project connection:** Session ownership, permission to publish audio, and
permission to apply a turn result solve different problems. Trace each identity
to the place where it is checked.

## 11. Sound Becomes Numbers

Sound is a changing physical signal. A microphone and conversion hardware
produce sampled numerical measurements. Sample rate is samples per second per
channel. A channel represents one stream, such as mono or one side of stereo.

PCM, pulse-code modulation, represents samples directly as numerical values.
Bit depth determines bits per sample. At 16,000 samples/second, 16 bits/sample,
and one channel, raw payload rate is 256,000 bits/second = 32,000 bytes/second.
A 20 ms frame contains 320 samples and 640 raw bytes. This excludes Python
objects, container overhead, packet headers, and codec effects.

A frame groups a short duration of samples for processing. A codec encodes or
decodes audio, often compressing it. Resampling changes the sample rate through
signal processing; changing a metadata label alone corrupts interpretation.

**Try:** Recalculate raw bytes per second for two channels. Why does compressed
network traffic not necessarily equal that number?

## 12. The Voice Conversation Pipeline

STT, speech-to-text, estimates words from audio. Partial results can be revised;
final results indicate a provider's completed segment, which is not necessarily
the whole conversational turn.

VAD, voice activity detection, estimates whether speech is present. Endpointing
decides when the user has finished a turn. Silence is useful evidence but may
just mean the speaker is pausing.

The agent runtime selects context and coordinates model/tool decisions.
TTS, text-to-speech, synthesizes audio from text. Chunking groups generated text
into speakable pieces. Playback sends or presents synthesized audio.

Barge-in means the caller interrupts while agent audio is playing. Stopping
generation is insufficient if older audio remains buffered. We track output
identity and delivery evidence so the next turn does not assume an unplayed
sentence was delivered.

**Try:** Trace “Move my appointment … actually, cancel it” while agent audio is
already playing. Identify separate speech, turn, tool, and playback decisions.

## 13. AI Models, Inference, and Tools

A model uses learned parameters to compute outputs from inputs. Training adjusts
parameters using data and an objective. Inference applies a trained model.
Neither term specifies whether the result is correct.

A language model processes tokens, units produced by a tokenizer; tokens do not
correspond one-to-one with words. Context is the input information supplied for
a particular generation, within model limits. A prompt is part of that input.

A tool call is a model-produced request for an application operation. The model
does not automatically gain permission to execute it. The runtime validates
arguments, checks authorization and business rules, and controls dispatch.

Embeddings represent inputs as numerical vectors useful for operations such as
similarity retrieval. Retrieval-augmented generation (RAG) obtains relevant
material and supplies it as context; it does not inherently retrain the model.
Retrieved text still requires appropriate trust and data-access treatment.

**Try:** A model confidently says “booked” without a successful tool result.
Which component must prevent that claim, and what evidence would justify it?

**Learning boundary:** This explains how models connect to the application.
Deriving model training requires further mathematics and dedicated lessons,
mapped in the learning path.

## 14. Testing, Evaluation, and Observation

A test runs a scenario and checks an expectation. A unit test isolates a small
rule; an integration test checks interacting components. A fake is a controlled
replacement used to exercise a contract. Passing a fake-based test does not
establish compatibility with an actual provider.

A log records an event or message. A metric summarizes measurements, such as
queue depth or error count. A trace connects operations that caused a request's
behavior. Observability helps infer internal behavior from these signals.

An evaluation measures behavior against a task and rubric. Checking the actual
appointment state is stronger evidence of a booking than judging fluent wording.
Model-assisted evaluation has its own uncertainty and needs calibration.

**Try:** Design one test for duplicate booking prevention and one measurement
for interruption delay. Explain why they need different evidence.

## 15. Latency, Throughput, and Experiments

Latency is elapsed time between explicitly chosen boundaries. Throughput is work
completed per unit time. Increasing throughput can worsen latency if work queues
up. A percentile describes a distribution: p95 is a boundary at or below which
approximately 95% of observations fall, subject to the estimator used.

Streaming stages overlap, so adding all stage durations can double-count time.
Measure total latency directly where possible and use causal spans to explain
the critical path: dependent operations that determine completion time.

A benchmark is a controlled workload with a recorded environment. A profiler
helps locate resource consumption and adds measurement overhead. An optimization
is justified by a measured problem and a comparison that preserves correctness.

**Try:** A call takes one second while using 20 ms of CPU time. List possible
sources of the remaining elapsed time. Do not assume the CPU needs optimization.

## 16. Packaging, Git, and Repeatable Work

A dependency is code the project relies on. A virtual environment isolates
Python package installations. A lockfile records selected dependency versions
and related resolution information for repeatability. A build produces an
installable artifact from source.

Git records snapshots and relationships between changes. A commit identifies
one recorded change set; a branch names a development line. Recording code does
not itself prove the tests ran. Continuous integration (CI) runs configured
checks when changes are submitted.

Configuration selects behavior without changing source code. Secrets such as
provider keys must not be confused with ordinary configuration values or copied
into learning logs.

**Try:** Explain why “works on my machine” is weaker evidence than a documented
installation and test run in a clean environment.

## 17. Worked Answers and Next Experiments

For the aliasing question, copying the outer list separates later appends, but
nested mutable objects remain shared after a shallow copy. Draw both reference
graphs before experimenting.

For the backlog question, a fixed item count cannot cap memory if each item can
be arbitrarily large. Track both payload limits and queue capacity.

For the booking timeout, the client knows it lacks a response; it cannot infer
whether the appointment was saved. Preserve the operation identity and obtain
evidence before choosing a retry.

For stereo PCM in the stated format, two channels use 64,000 raw bytes/second.
Compression, packet overhead, and framing change the actual network rate.

For the AI claim, an authoritative successful tool outcome is the evidence for
a committed booking. Fluent model text is insufficient.

The remaining prompts are discussion or experiment prompts, not assessed tests.
Future checkpoint notes must include their concrete variants, hints, and worked
solutions. Record your predictions, observations, and questions in the journal.
