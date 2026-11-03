# Spec Kit prompts for Part 1A

Paste these into your agent one at a time, in order. Save each output it produces.

## /speckit-constitution
Project: Smart Todo CLI (Python 3.11+).
Constraints to enforce:
- Lint: code must pass `ruff check` with zero errors.
- Security: code must pass `bandit -r src` with no medium or high severity findings.
- Tests: every acceptance criterion must map to at least one pytest test. Tests must never be deleted, skipped, or weakened to pass.
- Storage: tasks persist to a JSON file at a path given by the TODO_DATA_PATH environment variable (default ./data/tasks.json). No database.
- Dependencies: standard library only, plus pytest, ruff, bandit for development.
- No secrets, API keys, or credentials in code or committed files.

## /speckit-specify
Build a command-line todo manager with these features:
1. add "<title>" [--tag TAG] [--priority low|medium|high] creates a task with status "open" and a unique integer id. Returns the id.
2. list [--tag TAG] [--sort priority] shows tasks. Sorting by priority orders high, medium, low, then by id ascending.
3. complete <id> sets status to "done". Completing an already-done task is a no-op that exits 0.
4. delete <id> removes the task. Unknown id exits with code 1 and prints an error to stderr.
5. Task status transitions allowed: open -> done only. Any other transition is rejected with exit code 1.
6. Tags are case-insensitive. Filtering by tag returns only tasks containing that tag.
7. All data persists to JSON across invocations.
Acceptance criteria must be binary and testable (pass/fail for each).

## /speckit-clarify
Review the specification and list any ambiguities. For each, propose a single answer and record it in the spec. Specifically resolve: maximum title length, behavior on invalid priority, and what happens when the JSON file is missing or corrupt.

## /speckit-plan
Create a technical plan using Python standard library only. Define modules for the CLI, task model, storage adapter, and validation. Map each acceptance criterion to the module and test file that will verify it.

## /speckit-tasks
Break the plan into small ordered tasks. Each task must name the acceptance criterion it satisfies and the test that verifies it. Write tests before implementation tasks for each criterion.

## /speckit-analyze
Check consistency across spec, plan, and tasks. Report any criterion without a test or any task without a criterion.

## /speckit-implement
Implement the approved tasks only. Do not modify the spec, constitution, or existing tests to make them pass. If a test fails, report the failure and fix the implementation.
