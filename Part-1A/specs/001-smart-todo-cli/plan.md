# Implementation Plan: Smart Todo CLI

**Branch**: `001-smart-todo-cli` | **Date**: 2026-11-01 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-smart-todo-cli/spec.md`

## Summary

Implement a Python 3.11+ command-line todo manager with `add`, `list`, `complete`, and `delete` commands. Keep command parsing and output in a CLI module, task invariants in a task model and validation module, and persistence in a JSON storage adapter. Use only the Python standard library at runtime, with pytest, ruff, and bandit for development.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: Python standard library at runtime; pytest, ruff, and bandit for development only.

**Storage**: JSON file selected by `TODO_DATA_PATH`, defaulting to `./data/tasks.json`; no database.

**Testing**: pytest unit tests for task, validation, and storage behavior; subprocess-based CLI integration tests for user-visible commands and persistence.

**Target Platform**: Platforms supported by Python 3.11+.

**Project Type**: Command-line application.

**Performance Goals**: No special throughput or latency target is specified; operations should handle the stored task list without unnecessary work.

**Constraints**: Standard-library-only application code; titles are 1–200 Unicode code points and cannot be whitespace-only; priorities are lowercase `low`, `medium`, `high`, defaulting to `medium`; IDs are positive and never reused; corrupted or unreadable storage must not be modified; satisfy `ruff check` and `bandit -r src` with no medium or high severity findings.

**Scale/Scope**: Single-user local task list persisted to one JSON file; one optional tag and one priority per task.

## Constitution Check

- **Testable requirements**: Each AC-001–AC-012 criterion is mapped below to at least one pytest test.
- **CLI behavior**: Command syntax, stdout/stderr behavior, exit codes, and task state rules are implemented and tested at the CLI boundary where applicable.
- **Durable JSON storage**: The storage adapter uses only JSON files and resolves the configured path from the environment, with the specified default.
- **Minimal dependencies and security**: Runtime modules use the standard library only. Development dependencies are limited to pytest, ruff, and bandit; no credentials or secrets are needed.
- **Quality gates**: Before completion, run pytest, `ruff check`, and `bandit -r src`; do not weaken tests or requirements to obtain passing results.

## Design

### Module Responsibilities

- **`src/todo_cli/cli.py`**: Define the `argparse` interface and dispatch commands. Keep successful command output on stdout and errors on stderr. Return the specified exit codes and avoid output for successful `complete` and `delete`.
- **`src/todo_cli/task.py`**: Define the task data model and its lifecycle operation. Enforce the allowed `open` to `done` transition; reject every other transition. Keep task values explicit and typed.
- **`src/todo_cli/validation.py`**: Validate titles, priorities, IDs, task records, and persisted task structures. Preserve accepted title text exactly. Share validation rules between CLI input and storage loading.
- **`src/todo_cli/storage.py`**: Resolve the JSON path from `TODO_DATA_PATH`; load missing files as empty storage; reject unreadable, malformed, or structurally invalid data without modifying it. Persist task mutations and a monotonic next-ID value so deleted IDs are never reused.

### Persistence Shape

Use one JSON object with a `next_id` positive integer and a `tasks` array. Each task record stores `id`, `title`, `status`, `tag`, and `priority`; `tag` and `priority` may be null when absent. On load, validate the entire structure and reject invalid data. `next_id` must be greater than every ID already assigned as represented by the persisted state. A missing file starts as an empty collection with the initial ID of 1. Mutations write the updated collection and next ID to the configured path.

### Data and Control Flow

The CLI parses arguments, calls shared validators, delegates task operations to the model, and loads/saves through the storage adapter. Listing filters tags with case-insensitive comparison and sorts by `(priority rank, id)` when requested; without a sort option, it sorts by ID. The CLI formats each task line in the specified field order and uses `-` for absent optional values.

## Acceptance-Criteria Test Mapping

| Criterion | Implementation modules | Pytest verification |
|---|---|---|
| AC-001: Add task, open status, positive unique/non-reused IDs, exact stdout | `cli.py`, `task.py`, `storage.py`, `validation.py` | `tests/integration/test_cli.py::test_add_returns_unique_positive_id_and_open_task`; `tests/integration/test_cli.py::test_deleted_task_id_is_not_reused` |
| AC-002: Optional tag/priority and medium default | `cli.py`, `task.py`, `storage.py`, `validation.py` | `tests/integration/test_cli.py::test_add_stores_tag_and_explicit_priority`; `tests/integration/test_cli.py::test_add_defaults_priority_to_medium` |
| AC-003: Priority ordering with ID tie-break | `cli.py`, `task.py` | `tests/integration/test_cli.py::test_list_sorts_by_priority_then_id` |
| AC-004: Case-insensitive filtering, empty result, output fields | `cli.py`, `task.py` | `tests/integration/test_cli.py::test_list_filters_tags_case_insensitively`; `tests/integration/test_cli.py::test_list_no_matches_emits_no_task_lines`; `tests/integration/test_cli.py::test_list_formats_all_fields_and_missing_values` |
| AC-005: Complete open task; repeated completion is an unchanged no-op | `cli.py`, `task.py`, `storage.py` | `tests/integration/test_cli.py::test_complete_marks_task_done_without_output`; `tests/integration/test_cli.py::test_complete_done_task_is_noop` |
| AC-006: Accept only `open` to `done`; reject other transitions | `task.py` | `tests/unit/test_task.py::test_transition_open_to_done`; `tests/unit/test_task.py::test_rejects_transitions_other_than_open_to_done` |
| AC-007: Delete and unknown-ID error | `cli.py`, `storage.py` | `tests/integration/test_cli.py::test_delete_removes_existing_task_without_output`; `tests/integration/test_cli.py::test_delete_unknown_id_reports_error` |
| AC-008: Persistence across invocations; configured and default paths | `cli.py`, `storage.py` | `tests/integration/test_cli.py::test_tasks_persist_across_invocations`; `tests/integration/test_cli.py::test_default_storage_path_when_environment_unset` |
| AC-009: Title bounds and rejection of blank titles | `validation.py`, `cli.py` | `tests/unit/test_validation.py::test_title_length_boundaries`; `tests/integration/test_cli.py::test_add_rejects_empty_whitespace_and_overlong_titles` |
| AC-010: Invalid priority rejected without changing storage | `validation.py`, `cli.py`, `storage.py` | `tests/unit/test_validation.py::test_rejects_invalid_priority_values`; `tests/integration/test_cli.py::test_invalid_priority_does_not_change_storage` |
| AC-011: Missing storage is empty; bad storage errors without file changes | `storage.py`, `validation.py`, `cli.py` | `tests/unit/test_storage.py::test_missing_file_loads_empty_store`; `tests/integration/test_cli.py::test_invalid_storage_is_reported_without_modification` |
| AC-012: Completing unknown ID reports error | `cli.py`, `storage.py` | `tests/integration/test_cli.py::test_complete_unknown_id_reports_error` |

Every listed test is additive: implementation work must not delete, skip, or weaken acceptance tests. The test names above define the planned coverage and may be refined when the test files are created, provided all acceptance coverage is retained.

## Project Structure

### Documentation (this feature)

```text
specs/001-smart-todo-cli/
├── spec.md
├── plan.md
└── tasks.md              # Created during /speckit.tasks
```

### Source Code

```text
src/
└── todo_cli/
    ├── __init__.py
    ├── __main__.py       # Enables `python -m todo_cli`
    ├── cli.py
    ├── task.py
    ├── storage.py
    └── validation.py

tests/
├── unit/
│   ├── test_task.py
│   ├── test_storage.py
│   └── test_validation.py
└── integration/
    └── test_cli.py
```

**Structure Decision**: Use one small Python package under `src/todo_cli` and separate unit and subprocess integration tests under `tests/`. This directly matches the requested CLI, task model, storage adapter, and validation modules without introducing additional runtime packages or architectural layers.

## Implementation Sequence

1. Write the unit and integration tests mapped above before implementing their corresponding acceptance behavior.
2. Define task types and shared input/data validation.
3. Implement JSON loading, validation, persistence, path configuration, and monotonic IDs.
4. Implement CLI parsing, dispatch, formatting, and error/exit behavior.
5. Run pytest, `ruff check`, and `bandit -r src`; fix implementation findings without weakening tests or requirements.

## Complexity Tracking

No constitution violations or additional architectural complexity are proposed.
