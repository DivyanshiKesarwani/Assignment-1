# Smart Todo CLI Constitution

## Core Principles

### I. Testable Requirements
Every acceptance criterion MUST be binary and verifiable by at least one pytest test. Tests MUST be written to preserve the specified behavior; tests MUST NOT be deleted, skipped, or weakened to make an implementation pass. Specifications, plans, and task lists MUST keep each criterion traceable to its verifying test.

### II. Reliable CLI Behavior
The CLI MUST implement the approved command and task behavior consistently, including documented exit codes and error reporting. Invalid operations MUST fail explicitly rather than silently succeeding or changing task state.

### III. Durable JSON Storage
Task data MUST persist across invocations in a JSON file. The file path MUST come from `TODO_DATA_PATH`, defaulting to `./data/tasks.json` when the variable is unset. The application MUST NOT use a database.

### IV. Secure, Minimal Dependencies
Application code MUST use only the Python 3.11+ standard library. `pytest`, `ruff`, and `bandit` are permitted for development only. Code and committed files MUST NOT contain secrets, API keys, or credentials.

### V. Automated Quality Gates
All code changes MUST pass `ruff check` with zero errors and `bandit -r src` with no medium- or high-severity findings. Relevant pytest tests MUST pass before a change is considered complete. Failures MUST be fixed in the implementation, not hidden by weakening tests or quality gates.

## Technical Constraints

- The project targets Python 3.11 or later.
- Persistent task storage is JSON at the configured path; no database or non-standard runtime dependency is permitted.
- The development toolchain is limited to pytest, ruff, and bandit in addition to the standard library.
- Security scans apply to `src`; findings of medium or high severity are release-blocking.

## Development Workflow

- Define acceptance criteria as measurable pass/fail requirements and map each to one or more pytest tests.
- Keep specifications, plans, tasks, implementation, and tests consistent; implementation tasks must trace to approved requirements.
- Run the relevant pytest tests, `ruff check`, and `bandit -r src` before declaring work complete.
- Do not modify specifications, acceptance criteria, tests, or quality thresholds merely to obtain a passing result.

## Governance

This constitution governs project specifications, plans, tasks, implementation, and reviews. Any change to these principles or constraints MUST be explicit, documented, and reflected in affected project guidance. When requirements conflict, this constitution takes precedence unless it is formally amended.

**Version**: 1.0.0 | **Ratified**: 2026-11-01 | **Last Amended**: 2026-11-01
