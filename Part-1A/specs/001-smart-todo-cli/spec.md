# Feature Specification: Smart Todo CLI

**Feature Branch**: `001-smart-todo-cli`

**Created**: 2026-11-01

**Status**: Draft

**Input**: User description: "Build a command-line todo manager with add, list, complete, and delete commands; enforce task status transitions, case-insensitive tag filtering, and JSON persistence."

## User Scenarios & Testing

### User Story 1 - Create and view tasks (Priority: P1)

As a user, I can add tasks and list them so I can keep track of work to do.

**Why this priority**: Creating and viewing tasks is the minimum useful todo workflow.

**Independent Test**: Add tasks, then list them and verify their returned IDs and displayed task details.

**Acceptance Scenarios**:

1. **Given** no task with the newly assigned ID, **When** the user runs `add "<title>"`, **Then** the CLI creates an open task, prints its unique integer ID, and exits successfully.
2. **Given** an optional tag and/or priority, **When** the user runs `add "<title>" --tag TAG --priority PRIORITY`, **Then** the created task has the supplied tag and priority.
3. **Given** tasks with different priorities, **When** the user runs `list --sort priority`, **Then** tasks are shown in high, medium, low priority order, with tasks of equal priority ordered by ID ascending.
4. **Given** tasks with tags, **When** the user runs `list --tag TAG`, **Then** only tasks containing that tag are shown, regardless of tag letter case.

### User Story 2 - Complete tasks (Priority: P1)

As a user, I can mark an open task done and safely repeat that action.

**Why this priority**: Completing tasks is the central lifecycle action of a todo manager.

**Independent Test**: Add a task, complete it, and verify its status; complete it again and verify the command succeeds without changing it further.

**Acceptance Scenarios**:

1. **Given** an open task, **When** the user runs `complete <id>`, **Then** the task's status becomes `done`.
2. **Given** a task already in status `done`, **When** the user runs `complete <id>`, **Then** the command makes no further change and exits with code 0.
3. **Given** a requested status transition other than `open` to `done`, **When** the transition is attempted, **Then** it is rejected and the CLI exits with code 1.

### User Story 3 - Delete tasks (Priority: P2)

As a user, I can remove tasks I no longer need.

**Why this priority**: Deletion keeps the task list relevant, while the core add/list/complete workflow remains useful without it.

**Independent Test**: Add a task, delete it, and verify it is absent from the task list.

**Acceptance Scenarios**:

1. **Given** an existing task, **When** the user runs `delete <id>`, **Then** the task is removed.
2. **Given** an unknown task ID, **When** the user runs `delete <id>`, **Then** the command exits with code 1 and prints an error to stderr.

### User Story 4 - Keep tasks between invocations (Priority: P1)

As a user, I can close and rerun the CLI without losing my tasks.

**Why this priority**: Persistence is necessary for a useful todo manager.

**Independent Test**: Add a task in one CLI invocation and verify it is present in a separate invocation.

**Acceptance Scenarios**:

1. **Given** a task was added in an earlier invocation, **When** the user runs the CLI again and lists tasks, **Then** the task and its stored details are present.

## Edge Cases

- Filtering with a tag that matches no task produces no task entries.
- Tag matching is case-insensitive for both the stored tag and the filter.
- Deleting an unknown ID produces the specified error and exit code rather than silently succeeding.
- An empty or whitespace-only title is rejected; a title longer than 200 Unicode code points is rejected.
- A missing JSON file is treated as an empty task list. Corrupt or unreadable task data is reported without replacing the file.
- Completing an unknown ID fails with exit code 1 and an error on stderr.
- The CLI does not expose arbitrary status changes. The task status-transition operation rejects any transition other than `open` to `done`; if such a rejected transition is surfaced by a CLI operation, it exits with code 1.

## Requirements

### Functional Requirements

- **FR-001**: The CLI MUST provide `add "<title>" [--tag TAG] [--priority low|medium|high]`.
- **FR-002**: Adding a task MUST assign it a positive integer ID that is not reused after deletion, set its status to `open`, and print only that ID followed by a newline to stdout.
- **FR-003**: The CLI MUST provide `list [--tag TAG] [--sort priority]` and show matching tasks, one task per line, with ID, title, status, tag, and priority fields in that order. Missing optional tag or priority values MUST display as `-`. An empty result MUST produce no task lines and exit 0.
- **FR-004**: When sorting by priority, the CLI MUST order tasks as high, medium, then low; tasks with the same priority MUST be ordered by ID ascending.
- **FR-005**: Tag comparisons MUST be case-insensitive. Filtering by tag MUST return only tasks containing the matching tag.
- **FR-006**: The CLI MUST provide `complete <id>` to change an open task's status to `done`. Completing a task already marked `done` MUST be a no-op that exits with code 0. Completing an unknown ID MUST exit with code 1 and print an error to stderr.
- **FR-007**: Only the `open` to `done` status transition is allowed. The task status-transition operation MUST reject any other requested transition; if invoked through the CLI, rejection MUST exit with code 1 and print an error to stderr. The CLI MUST NOT add a command for arbitrary status changes.
- **FR-008**: The CLI MUST provide `delete <id>` to remove a task. Deleting an unknown ID MUST exit with code 1 and print an error to stderr.
- **FR-009**: Task data MUST persist as JSON across separate CLI invocations at the path specified by `TODO_DATA_PATH`, defaulting to `./data/tasks.json`.
- **FR-010**: A title MUST contain between 1 and 200 Unicode code points inclusive; whitespace-only titles and longer titles MUST be rejected with exit code 1 and an error on stderr. Accepted titles MUST be stored without trimming or alteration.
- **FR-011**: The only valid explicit priorities are the lowercase values `low`, `medium`, and `high`. An invalid value MUST be rejected with exit code 1 and an error on stderr, without changing stored tasks. If priority is omitted, it MUST default to `medium`.
- **FR-012**: If the configured JSON file does not exist, the CLI MUST treat storage as an empty task list. If the file is unreadable, invalid JSON, or does not contain valid task data, commands MUST exit with code 1, print an error to stderr, and leave the file unchanged.
- **FR-013**: Successful `complete` and `delete` commands MUST exit 0. Successful `complete` MUST produce no output. Successful `delete` MUST produce no output.

### Acceptance Criteria

Each criterion has an observable pass/fail outcome. Each MUST be covered by at least one pytest test before implementation is considered complete.

- **AC-001 (FR-001, FR-002)**: Running `add "Buy milk"` exits 0, prints only a positive integer ID and newline to stdout, and stores a task with title `Buy milk` and status `open`. Adding another task produces a different ID. Deleting a task and adding another never reuses a previously assigned ID.
- **AC-002 (FR-001, FR-002, FR-011)**: Running `add "Buy milk" --tag Work --priority high` exits 0 and stores the supplied tag and priority. Omitting priority stores `medium`.
- **AC-003 (FR-003, FR-004)**: Given tasks with high, medium, and low priorities and distinct IDs, `list --sort priority` displays them in high/medium/low order; within each priority, displayed IDs are ascending.
- **AC-004 (FR-003, FR-005)**: Given tasks tagged `Work` and `home`, `list --tag wOrK` displays only tasks tagged `Work`; a filter with no matching tag exits 0 and emits no task lines. Every displayed task line contains ID, title, status, tag, and priority in that order; absent optional values display as `-`.
- **AC-005 (FR-006, FR-013)**: Completing an open task changes its stored status to `done`, exits 0, and emits no output. Completing that task again exits 0, emits no output, and leaves its stored task data unchanged.
- **AC-006 (FR-007)**: A task status-transition operation accepts `open` to `done`; it rejects `done` to `open` and every other transition. A rejected transition is represented as an error; if a CLI operation invokes that rejected transition, the CLI exits 1 and writes the error to stderr. No arbitrary-status command is available.
- **AC-007 (FR-008, FR-013)**: Deleting an existing task removes it, exits 0, and emits no output; deleting an unknown ID exits 1 and writes an error to stderr.
- **AC-008 (FR-009)**: A task created in one CLI invocation at the path configured by `TODO_DATA_PATH` is still present, with its stored details, when listed in a separate invocation using the same path. When the variable is unset, the CLI uses `./data/tasks.json`.
- **AC-009 (FR-010)**: A title of 1 or 200 Unicode code points is accepted and stored exactly as supplied. An empty title, a whitespace-only title, or a title of 201 code points exits 1, writes an error to stderr, and does not create a task.
- **AC-010 (FR-011)**: Each explicit priority other than lowercase `low`, `medium`, or `high` exits 1, writes an error to stderr, and leaves stored tasks unchanged.
- **AC-011 (FR-012)**: With a missing configured JSON file, listing exits 0 with no task lines. With unreadable, invalid JSON, or structurally invalid task data, a command exits 1, writes an error to stderr, and leaves the file byte-for-byte unchanged.
- **AC-012 (FR-006)**: Completing an unknown ID exits 1 and writes an error to stderr.

### Key Entities

- **Task**: A todo item with a unique integer ID, title, status (`open` or `done`), and optional tag and priority (`low`, `medium`, or `high`).

## Success Criteria

### Measurable Outcomes

- **SC-001**: All acceptance criteria AC-001 through AC-012 pass their mapped pytest tests.
- **SC-002**: Tasks created in one invocation are retrievable from a later invocation using the same storage location.

## Assumptions

- The project is a command-line application; a graphical interface is out of scope.
- Tags and priorities are optional inputs to task creation.
- A task has at most one tag and one priority because the specified add command accepts one value for each.
- The supported task statuses are `open` and `done`.
- When priority is omitted, it defaults to `medium`; when list sorting is omitted, tasks are shown by ID ascending.
- The JSON file path is configured by `TODO_DATA_PATH`, with `./data/tasks.json` as the default. Missing storage means an empty task list; corrupt or unreadable storage is an error and is never automatically replaced.
- IDs are positive integers and are never reused, including after deletion.
- Error messages are written to stderr; the exact wording is not part of the contract.

## Clarification Decisions

- **Title length and blanks**: Titles may contain 1 through 200 Unicode code points inclusive. Empty or whitespace-only titles are rejected; accepted title text is stored exactly as supplied.
- **Invalid priority**: Only lowercase `low`, `medium`, and `high` are valid. Any other explicit value is rejected with exit code 1 and an error on stderr, without changing stored tasks. Omitted priority defaults to `medium`.
- **Missing or corrupt JSON**: A missing file represents an empty task list. Unreadable, invalid, or structurally invalid data is an error: exit 1, stderr message, and no modification or replacement of the file.
- **Status transition surface**: No command for arbitrary status changes is added. The task status-transition operation accepts only `open` to `done`; it rejects all other transitions. Rejection is reported as a CLI error (exit 1 and stderr) if surfaced by a CLI operation. Repeating `complete` on a `done` task remains the explicitly specified successful no-op.
- **Defaults and identifiers**: Omitted priority is `medium`; an unsorted list is ordered by ID ascending. IDs are positive integers and are never reused, even after deletion.
- **List output**: Each result is one line containing ID, title, status, tag, and priority in that order. Missing tag or priority is printed as `-`; no matching tasks produces no task lines and exits 0.
- **Unknown IDs and successful mutations**: Completing or deleting an unknown ID exits 1 and prints an error to stderr. Successful complete and delete operations exit 0 without output. Exact error wording is unspecified.
