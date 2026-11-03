# Feature Specification: Natural-Language Reminder Agent

**Feature Branch**: `001-reminder-agent`

**Created**: 2026-11-03

**Status**: Draft

**Input**: User description: "Build a CLI that takes one natural-language sentence and returns a JSON object describing a create, reschedule, snooze, clarify, or refuse reminder intent."

## User Scenarios & Testing

### User Story 1 - Create a reminder (Priority: P1)

As a user, I can describe a reminder in natural language and receive a structured reminder with its title and due date/time.

**Why this priority**: Creating reminders is the agent's primary user value.

**Independent Test**: Pass a valid create sentence to the CLI and validate its JSON response against the output contract and matching evaluation cases.

**Acceptance Scenarios**:

1. **Given** a sentence with an identifiable reminder and time, **When** it is submitted, **Then** the response identifies `create`, extracts the reminder title, and returns a parseable due date/time.
2. **Given** a create request with no usable time, **When** it is submitted, **Then** the response asks a clarification question instead of inventing a due time.
3. **Given** a recurring reminder phrase, **When** it is submitted, **Then** the agent extracts its reminder and time without executing or scheduling anything itself.

### User Story 2 - Change an existing reminder (Priority: P1)

As a user, I can ask to reschedule or snooze a reminder and receive a structured response that identifies which reminder and time are meant.

**Why this priority**: Existing reminders need natural-language time changes as well as creation.

**Independent Test**: Submit reschedule and snooze sentences and verify intent and reminder-title extraction against the evaluation cases.

**Acceptance Scenarios**:

1. **Given** a request to snooze a named reminder, **When** it is submitted, **Then** the response identifies `snooze` and extracts the reminder title.
2. **Given** a request to move a named reminder, **When** it is submitted, **Then** the response identifies `reschedule` and extracts the reminder title.

### User Story 3 - Resolve unclear or malformed input safely (Priority: P1)

As a user, I receive a clarification question for incomplete or malformed requests and a refusal for unsafe requests.

**Why this priority**: Reliable clarification and safe handling are essential when interpreting non-deterministic model output.

**Independent Test**: Submit ambiguous, empty, malformed-time, and adversarial inputs and validate the returned JSON structure, intent, and semantic checks.

**Acceptance Scenarios**:

1. **Given** empty, malformed, or ambiguous input, **When** it is submitted, **Then** the response identifies `clarify` and asks a relevant question when more information is needed.
2. **Given** a request to bypass rules or execute an operating-system command, **When** it is submitted, **Then** the agent refuses or ignores the unsafe instruction and never executes it.
3. **Given** a message containing a safe reminder and an unsafe command, **When** it is submitted, **Then** the agent may extract only the safe reminder and MUST NOT act on the command.

## Output Contract

For each input sentence, the CLI MUST write exactly one JSON object to stdout, followed by a newline, with exactly these four keys:

```json
{
  "intent": "create",
  "title": "Call mom",
  "due_datetime": "2026-11-04T17:00:00+00:00",
  "clarification_question": null
}
```

- `intent`: required string; one of `create`, `reschedule`, `snooze`, `clarify`, or `refuse`.
- `title`: required string or JSON `null`. When present, it contains the reminder action/name only, without command wording or due-time wording.
- `due_datetime`: required string or JSON `null`. When present, it MUST be a valid ISO 8601 date-time with a UTC offset. When no timezone is stated, timestamps MUST use UTC (`+00:00`).
- `clarification_question`: required string or JSON `null`. It MUST be a concise, relevant, non-empty question for `clarify`; for every other intent it MUST be `null`.

The CLI MUST NOT emit Markdown fences, commentary, extra keys, or multiple JSON values on stdout. Errors communicating with the model or parsing an unusable response MUST be surfaced on stderr and MUST NOT be converted into a fabricated success-shaped response.

### Structural Invariants

- **INV-1 — Create title**: A `create` response MUST contain a non-empty string title.
- **INV-2 — Missing create time**: A `create` response MUST contain a non-null due time. If a create request has no usable time, the agent MUST return `clarify` with a non-empty clarification question rather than `create`.
- **INV-3 — Expected intent**: The response intent MUST match the expected intent for each evaluation case in `evals/dataset.json`.
- **INV-4 — Adversarial guardrail**: Case `G01` MUST return `refuse`. No input may cause the application to execute commands or change actual reminders. Unsafe instructions embedded beside a separable safe reminder MUST be ignored while only the safe reminder is processed.

The independent validator MUST additionally enforce the Output Contract's exact key set, allowed intent values, JSON field types, ISO 8601 parseability, and intent-specific clarification-question rules before returning any response. `create`, `reschedule`, and `snooze` require a non-empty title and a non-null due time; `clarify` requires a non-empty question and may have a null title and due time; `refuse` has null due time and null question, and may have a null title. These validation rules are required even where the evaluation harness does not independently check every property.

### Semantic Check

- **SEM-1 — Meaning and extraction**: The response intent MUST match the user's apparent request; the title MUST identify the requested reminder rather than copy unrelated command or time text; a non-null due time MUST correspond to the input's stated time; and unsafe instructions MUST NOT be followed. For evaluation cases, the expected intent and all listed `title_keywords` in `evals/dataset.json` MUST match the response according to the harness checks.

## Evaluation Contract

The evaluation dataset is the fixed `evals/dataset.json` file. It contains 16 cases. The harness at `.harness/run_eval.py` is authoritative for evaluating schema, invariants, and semantic checks; neither the dataset nor the harness may be changed to obtain a pass.

**Pass threshold**: `0.90`. The score is `passed cases / total cases`; the overall evaluation passes when the score is at least 0.90. With 16 cases, at least 15 MUST pass (`15/16 = 0.9375`; `14/16 = 0.875`). This threshold MUST NOT be lowered after evaluation.

## Acceptance Criteria

Every criterion MUST be covered by the named immutable evaluation cases. Each case passes only when all checks performed by the harness pass.

- **AC-001 — Timed create extraction**: For cases `N01`, `N02`, `N03`, `N04`, `B01`, and `B02`, the response passes INV-1–INV-4 and SEM-1, uses the expected `create` intent, and includes the case's expected title keywords. `N03` and `N04` cover recurring reminder language and MUST represent only the next occurrence; `B01` is resolved from the processing-time UTC instant; `B02` covers an explicit calendar date.
- **AC-002 — Snooze and reschedule extraction**: For cases `R01` and `R02`, the response passes INV-1–INV-4 and SEM-1, uses the expected `snooze` or `reschedule` intent, includes the expected title keywords, and returns a due time resolved according to the UTC rules.
- **AC-003 — Ambiguity and missing time**: For cases `A01`, `A02`, `M01`, and `M02`, the response passes INV-1–INV-4 and SEM-1 and uses the expected `clarify` intent. A safe reminder title is retained when the case provides expected title keywords; a relevant clarification question is supplied.
- **AC-004 — Malformed or empty input**: For cases `F01` and `F02`, the response passes INV-1–INV-4 and SEM-1 and uses the expected `clarify` intent; it MUST NOT invent a valid time for malformed or empty input.
- **AC-005 — Unsafe instructions**: For `G01`, the response passes INV-1–INV-4 and SEM-1, uses expected intent `refuse`, and does not execute or claim to execute the requested deletion. For `G02`, the response MUST ignore the unsafe command, preserve the safe call reminder as `create`, and pass all harness checks including the expected title keywords.
- **AC-006 — Overall evaluation threshold**: The unmodified harness reports overall PASS only when at least 15 of the 16 cases pass all checks, yielding a score greater than or equal to 0.90.

## Functional Requirements

- **FR-001**: The CLI MUST accept one natural-language sentence and return the output contract as one JSON object.
- **FR-002**: The system MUST support `create`, `reschedule`, `snooze`, `clarify`, and `refuse` intents.
- **FR-003**: The system MUST extract the reminder title and due date/time for create, reschedule, and snooze requests when supported by the input.
- **FR-004**: A create request without a usable time MUST produce `clarify`, not an invented due time.
- **FR-005**: Empty, malformed, or ambiguous input MUST produce `clarify`.
- **FR-006**: Unsafe requests to bypass rules or run commands MUST be refused or ignored. A safe reminder embedded alongside an unsafe command MAY be processed without acting on the unsafe command.
- **FR-007**: Model output MUST be parsed and independently validated against INV-1–INV-4 and SEM-1 before being returned.
- **FR-008**: The system MUST use the fixed evaluation dataset and harness without weakening either or removing cases.
- **FR-009**: The evaluation threshold MUST be 0.90 using the score defined above.

## Edge Cases

- Time-only inputs without an explicit date are resolved to the next future occurrence of that time in UTC.
- A named weekday is resolved to its next future occurrence in UTC; if it is that weekday and the stated time has already passed, use the following week's occurrence.
- An invalid or impossible date/time yields `clarify` with `due_datetime: null`; never normalize it into a different valid time.
- A request containing multiple independent reminders yields `clarify` and asks which single reminder to handle; do not silently discard all but one.
- A reschedule or snooze request without a resolvable target time yields `clarify`, keeps the identifiable reminder title if possible, and asks for the missing target time.
- For a snooze request that names the reminder's current time and a delay (for example, "snooze my 3pm meeting reminder by 20 minutes"), resolve the target to the next future occurrence of that named time plus the delay. If the original time or delay cannot be resolved, clarify.
- A safe reminder accompanied by a separable command or instruction to override rules may be extracted as a create reminder, but unsafe text is never included as a requested action and is never executed.

## Clarification Decisions

- **Timezone**: All date/time values use UTC. Inputs with an explicit timezone are converted to UTC; inputs without one are interpreted as UTC. Every non-null `due_datetime` includes the `+00:00` offset.
- **Relative times**: Relative expressions are calculated from the UTC clock instant captured once when the input is processed. Durations such as "in 2 hours" add the stated duration to that instant. Calendar expressions such as "tomorrow" and weekdays are resolved in UTC using that same reference instant. A weekday refers to its next future occurrence; if its time has passed on that weekday, resolve to the next week.
- **Recurring reminders**: The required output schema has no recurrence field. Treat a recurring request as a one-time reminder for its next occurrence, return that occurrence's due time, and do not claim that future recurrences have been scheduled.
- **Multiple reminders**: The output permits one reminder only. If an input requests multiple distinct reminders, return `clarify`, set `title` and `due_datetime` to `null`, and ask which reminder to handle first.
- **Missing reschedule/snooze time**: Return `clarify`, preserve the existing reminder title when identifiable, set `due_datetime` to `null`, and ask for the target time. Do not return `reschedule` or `snooze` with a missing target.
- **Snooze delay**: If the input identifies the existing reminder time and a snooze delay, the due time is that next future reminder occurrence plus the delay. If it gives only a delay, the due time is the processing-time UTC instant plus the delay.
- **Date-only reschedule**: When a reschedule request specifies a date but no clock time, use 09:00 UTC on that date. This supplies the due time for evaluation case R02.
- **Malformed or empty input**: Return `clarify` with `due_datetime: null`; retain a safe identifiable title if one exists, otherwise use `null`, and include a concise question.
- **Unsafe content**: Refuse requests whose primary intent is to bypass rules or perform unsafe actions. If a benign reminder is separable from an unsafe command, process only the benign reminder and ignore the command.

## Success Criteria

- **SC-001**: All returned application responses are valid against the output contract and independently checked before use.
- **SC-002**: The fixed evaluation achieves a score of at least 0.90, meaning at least 15 of 16 cases pass all harness checks.
- **SC-003**: No evaluation case is deleted or skipped, and neither the dataset nor the harness is modified to increase the score.

## Assumptions

- The application interprets one input sentence per invocation and emits one response object per invocation. Inputs with multiple requested reminders are clarified rather than partially processed.
- The application classifies and extracts reminder information only; it does not create, modify, delete, or schedule actual reminders.
- Evaluation cases and their expected intent/title keywords are read from `evals/dataset.json` and remain unchanged.
- Time interpretation uses UTC and a single processing-time clock snapshot per input.
- Recurrence is outside the output schema and only the next occurrence is represented.
