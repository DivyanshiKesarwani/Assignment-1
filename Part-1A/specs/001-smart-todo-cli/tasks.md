# Tasks: Smart Todo CLI

**Input**: Design documents from `specs/001-smart-todo-cli/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md)

**Testing**: Every acceptance criterion has an explicit pytest task before its implementation task. Tests must fail against the not-yet-implemented behavior, then pass after implementation. Tests MUST NOT be deleted, skipped, or weakened.

**Organization**: Tasks are ordered by user story and acceptance criterion. Complete each test task before its paired implementation task.

## Phase 1: User Story 1 - Create and view tasks (Priority: P1)

**Goal**: Add tasks and list them with the specified fields, sorting, and tag filtering.

**Independent Test**: Exercise add and list commands in isolated temporary storage and inspect output and persisted JSON.

### AC-001 - Add tasks with unique, non-reused IDs

- [x] T001 [US1] Write the AC-001 integration tests `test_add_returns_unique_positive_id_and_open_task` and `test_deleted_task_id_is_not_reused` in `tests/integration/test_cli.py`; verify exact stdout, open status, distinct IDs, and no ID reuse after deletion.
- [x] T002 [US1] Implement the AC-001 task creation path in `src/todo_cli/task.py`, `src/todo_cli/storage.py`, and `src/todo_cli/cli.py`; assign positive IDs, persist new open tasks with a monotonic next-ID value, and print only the ID and newline. Verify the add behavior with `tests/integration/test_cli.py::test_add_returns_unique_positive_id_and_open_task`; verify non-reuse after deletion once AC-007 is implemented in T016.

### AC-002 - Optional tag and priority defaults

- [x] T003 [US1] Write the AC-002 integration tests `test_add_stores_tag_and_explicit_priority` and `test_add_defaults_priority_to_medium` in `tests/integration/test_cli.py`. Verify with those tests that supplied values persist and omitted priority is `medium`.
- [x] T004 [US1] Implement the AC-002 optional tag and priority handling in `src/todo_cli/cli.py`, `src/todo_cli/task.py`, and `src/todo_cli/storage.py`. Verify with `tests/integration/test_cli.py::test_add_stores_tag_and_explicit_priority` and `tests/integration/test_cli.py::test_add_defaults_priority_to_medium`.

### AC-003 - Priority sorting

- [x] T005 [US1] Write `tests/integration/test_cli.py::test_list_sorts_by_priority_then_id` for AC-003, asserting high/medium/low ordering and ascending IDs within each priority.
- [x] T006 [US1] Implement AC-003 list sorting in `src/todo_cli/cli.py`; verify the ordering and tie-break with `tests/integration/test_cli.py::test_list_sorts_by_priority_then_id`.

### AC-004 - Tag filtering and list formatting

- [x] T007 [US1] Write the AC-004 integration tests `test_list_filters_tags_case_insensitively`, `test_list_no_matches_emits_no_task_lines`, and `test_list_formats_all_fields_and_missing_values` in `tests/integration/test_cli.py`.
- [x] T008 [US1] Implement AC-004 case-insensitive filtering and specified task-line formatting in `src/todo_cli/cli.py`; verify with `tests/integration/test_cli.py::test_list_filters_tags_case_insensitively`, `tests/integration/test_cli.py::test_list_no_matches_emits_no_task_lines`, and `tests/integration/test_cli.py::test_list_formats_all_fields_and_missing_values`.

## Phase 2: User Story 2 - Complete tasks (Priority: P1)

**Goal**: Complete open tasks, enforce the task transition rule, and report unknown IDs.

**Independent Test**: Complete tasks using the CLI and exercise the task transition operation directly.

### AC-005 - Complete an open task and make repeat completion a no-op

- [x] T009 [US2] Write AC-005 integration tests `test_complete_marks_task_done_without_output` and `test_complete_done_task_is_noop` in `tests/integration/test_cli.py`; assert persisted status, no command output, and unchanged stored data on repeat.
- [x] T010 [US2] Implement AC-005 completion behavior in `src/todo_cli/task.py`, `src/todo_cli/storage.py`, and `src/todo_cli/cli.py`; verify with `tests/integration/test_cli.py::test_complete_marks_task_done_without_output` and `tests/integration/test_cli.py::test_complete_done_task_is_noop`.

### AC-006 - Reject invalid status transitions

- [x] T011 [US2] Write AC-006 unit tests `test_transition_open_to_done` and `test_rejects_transitions_other_than_open_to_done` in `tests/unit/test_task.py`; verify the allowed transition and rejection of all other transitions.
- [x] T012 [US2] Implement AC-006 transition validation in `src/todo_cli/task.py`; verify with `tests/unit/test_task.py::test_transition_open_to_done` and `tests/unit/test_task.py::test_rejects_transitions_other_than_open_to_done`.

### AC-012 - Complete an unknown ID

- [x] T013 [US2] Write `tests/integration/test_cli.py::test_complete_unknown_id_reports_error` for AC-012; assert exit code 1 and an error on stderr.
- [x] T014 [US2] Implement AC-012 unknown-ID handling in `src/todo_cli/storage.py` and `src/todo_cli/cli.py`; verify with `tests/integration/test_cli.py::test_complete_unknown_id_reports_error`.

## Phase 3: User Story 3 - Delete tasks (Priority: P2)

**Goal**: Remove existing tasks and report missing IDs.

**Independent Test**: Delete a task and verify that it is absent from subsequent list output.

### AC-007 - Delete existing and unknown IDs

- [x] T015 [US3] Write AC-007 integration tests `test_delete_removes_existing_task_without_output` and `test_delete_unknown_id_reports_error` in `tests/integration/test_cli.py`; assert removal, success output behavior, and error exit behavior.
- [x] T016 [US3] Implement AC-007 deletion and unknown-ID handling in `src/todo_cli/storage.py` and `src/todo_cli/cli.py`; verify with `tests/integration/test_cli.py::test_delete_removes_existing_task_without_output`, `tests/integration/test_cli.py::test_delete_unknown_id_reports_error`, and the AC-001 regression `tests/integration/test_cli.py::test_deleted_task_id_is_not_reused`.

## Phase 4: User Story 4 - Keep tasks between invocations (Priority: P1)

**Goal**: Persist task data to the configured JSON file and handle missing or invalid data safely.

**Independent Test**: Run separate CLI processes with the same temporary storage path and verify task persistence and error handling.

### AC-008 - Persist tasks and honor storage path configuration

- [x] T017 [US4] Write AC-008 integration tests `test_tasks_persist_across_invocations` and `test_default_storage_path_when_environment_unset` in `tests/integration/test_cli.py`; verify configured and default paths.
- [x] T018 [US4] Implement AC-008 path resolution and cross-invocation JSON persistence in `src/todo_cli/storage.py`, integrated through `src/todo_cli/cli.py`; verify with `tests/integration/test_cli.py::test_tasks_persist_across_invocations` and `tests/integration/test_cli.py::test_default_storage_path_when_environment_unset`.

### AC-009 - Validate title length and contents

- [x] T019 [US4] Write AC-009 unit and integration tests `test_title_length_boundaries` in `tests/unit/test_validation.py` and `test_add_rejects_empty_whitespace_and_overlong_titles` in `tests/integration/test_cli.py`.
- [x] T020 [US4] Implement AC-009 title validation in `src/todo_cli/validation.py` and apply it in `src/todo_cli/cli.py`; verify with `tests/unit/test_validation.py::test_title_length_boundaries` and `tests/integration/test_cli.py::test_add_rejects_empty_whitespace_and_overlong_titles`.

### AC-010 - Reject invalid priorities

- [x] T021 [US4] Write AC-010 tests `test_rejects_invalid_priority_values` in `tests/unit/test_validation.py` and `test_invalid_priority_does_not_change_storage` in `tests/integration/test_cli.py`.
- [x] T022 [US4] Implement AC-010 priority validation in `src/todo_cli/validation.py` and apply it before storage mutation in `src/todo_cli/cli.py`; verify with `tests/unit/test_validation.py::test_rejects_invalid_priority_values` and `tests/integration/test_cli.py::test_invalid_priority_does_not_change_storage`.

### AC-011 - Handle missing, invalid, and unreadable JSON

- [x] T023 [US4] Write AC-011 tests `test_missing_file_loads_empty_store` in `tests/unit/test_storage.py` and `test_invalid_storage_is_reported_without_modification` in `tests/integration/test_cli.py`; cover missing, unreadable, invalid JSON, and structurally invalid data.
- [x] T024 [US4] Implement AC-011 JSON loading and structural validation in `src/todo_cli/storage.py` and `src/todo_cli/validation.py`; ensure failures do not rewrite the file and verify with `tests/unit/test_storage.py::test_missing_file_loads_empty_store` and `tests/integration/test_cli.py::test_invalid_storage_is_reported_without_modification`.

## Phase 5: Quality Gates

**Purpose**: Verify the full implementation against all acceptance criteria and constitution requirements.

- [x] T025 Run all tests in `tests/unit/test_task.py`, `tests/unit/test_storage.py`, `tests/unit/test_validation.py`, and `tests/integration/test_cli.py` covering AC-001 through AC-012; run `ruff check` with zero errors and `bandit -r src` with no medium or high severity findings; fix implementation issues without deleting, skipping, or weakening tests.

## Dependencies & Execution Order

- Within every AC pair, write and run its test task before starting its implementation task.
- Complete tasks in listed order. Later CLI integration tests may depend on the command and storage behavior implemented for earlier acceptance criteria.
- AC-006 is verified directly against the task model because the CLI intentionally exposes no arbitrary-status command.
- T025 depends on all implementation tasks.
