# Tasks: Natural-Language Reminder Agent

**Input**: Design documents from `specs/001-reminder-agent/`

**Prerequisites**: [spec.md](./spec.md), [plan.md](./plan.md)

**Organization**: Tasks are ordered by prerequisite and user story. Every task names the functional requirement, invariant, semantic check, or evaluation case it satisfies. Tests precede implementation for the behavior they verify. The evaluation harness and `evals/dataset.json` are immutable.

## Phase 1: Setup and Contract Foundation

**Purpose**: Establish testable project interfaces and typed output rules.

- [ ] T001 [US1] Create the planned `src/reminder_agent/` package, `src/__init__.py`, `src/cli.py`, and `tests/unit/`, `tests/integration/`, and `tests/evaluation/` directories; supports FR-001 and the README CLI entry point.
- [ ] T002 [P] [US3] Write schema and field-type tests in `tests/unit/test_validation.py` for INV-1 and the exact four-key output contract.
- [ ] T003 [US3] Implement response keys, allowed intents, field types, and typed validation errors in `src/reminder_agent/validation.py`; satisfies INV-1 and FR-007, verified by T002.
- [ ] T004 [P] [US3] Write JSON decoding tests in `tests/unit/test_parser.py` for valid one-object output and rejection of empty, fenced, truncated, non-object, extra-text, and duplicate-key output; supports FR-007.
- [ ] T005 [US3] Implement strict JSON decoding in `src/reminder_agent/parser.py`; reject ambiguous or malformed serialization, verified by T004 and required by FR-007.
- [ ] T006 [P] [US3] Write deterministic UTC conversion and time-normalization tests in `tests/unit/test_time_utils.py` for explicit offsets, naive input policy, next-future weekday behavior, date-only reschedule default, and single reference-time anchoring; satisfies the UTC clarifications and AC-001/AC-002.
- [ ] T007 [US3] Implement the aware UTC reference clock and deterministic date-time normalization in `src/reminder_agent/time_utils.py`; satisfy the UTC and relative-time decisions including 09:00 UTC for date-only reschedules, verified by T006.

## Phase 2: User Story 1 - Create a Reminder (Priority: P1)

**Goal**: Extract a single reminder title and a valid UTC time.

### INV-1 and INV-2 - Required create title and time

- [ ] T008 [P] [US1] Add validator tests `test_create_requires_nonempty_title`, `test_create_requires_due_time`, and `test_clarify_requires_question` to `tests/unit/test_validation.py`; covers INV-1, INV-2, and FR-004.
- [ ] T009 [US1] Enforce intent-specific title, due-time, and clarification-question constraints in `src/reminder_agent/validation.py`; satisfies INV-1, INV-2, and FR-004, verified by T008.

### Evaluation cases N01, N02, N03, N04, B01, B02

- [ ] T010 [P] [US1] Add prompt construction tests in `tests/unit/test_prompt.py` requiring one JSON object, title/time extraction, UTC resolution, and next-occurrence-only handling for recurring requests; covers SEM-1 and AC-001.
- [ ] T011 [US1] Implement contract, extraction, UTC, recurrence, and no-invention instructions in `src/reminder_agent/prompt.py`; supports AC-001 and cases N01, N02, N03, N04, B01, B02, verified by T010.
- [ ] T012 [P] [US1] Add dataset-driven tests for N01 and N02 in `tests/evaluation/test_cases.py`; covers AC-001 normal timed create extraction.
- [ ] T013 [US1] Verify N01 and N02 outputs satisfy expected `create` intent, title keywords, and contract checks through `src/reminder_agent/agent.py` and `src/reminder_agent/validation.py`; satisfies cases N01 and N02, verified by T012.
- [ ] T014 [P] [US1] Add dataset-driven tests for N03 and N04 in `tests/evaluation/test_cases.py`; covers AC-001 recurring reminder extraction without claiming recurrence support.
- [ ] T015 [US1] Verify N03 and N04 next-occurrence outputs through `src/reminder_agent/prompt.py`, `src/reminder_agent/time_utils.py`, and `src/reminder_agent/validation.py`; satisfies cases N03 and N04, verified by T014.
- [ ] T016 [P] [US1] Add dataset-driven tests for B01 and B02 in `tests/evaluation/test_cases.py`; covers AC-001 relative-duration and explicit-date boundary inputs.
- [ ] T017 [US1] Verify B01 and B02 time extraction and title keywords through `src/reminder_agent/time_utils.py`, `src/reminder_agent/prompt.py`, and `src/reminder_agent/validation.py`; satisfies cases B01 and B02, verified by T016.

## Phase 3: User Story 2 - Reschedule and Snooze (Priority: P1)

**Goal**: Identify the intent, target reminder, and resolved due time for changes.

### Evaluation cases R01 and R02

- [ ] T018 [P] [US2] Add dataset-driven tests for R01 and R02 in `tests/evaluation/test_cases.py`; assert expected snooze/reschedule intent and title keywords, covering AC-002.
- [ ] T019 [US2] Implement prompt guidance for reminder target extraction and snooze-delay semantics in `src/reminder_agent/prompt.py` and `src/reminder_agent/time_utils.py`; satisfies AC-002 and cases R01/R02, verified by T018.
- [ ] T020 [US2] Enforce non-empty title and due time for `snooze` and `reschedule` responses in `src/reminder_agent/validation.py`; satisfies the output-contract validation for AC-002.

## Phase 4: User Story 3 - Clarify, Refuse, and Preserve Guardrails (Priority: P1)

**Goal**: Handle ambiguity, malformed inputs, and unsafe instructions without violating the output contract.

### Evaluation cases A01, A02, M01, M02, F01, F02

- [ ] T021 [P] [US3] Add dataset-driven tests for A01 and A02 in `tests/evaluation/test_cases.py`; covers AC-003 ambiguity with and without an identifiable reminder.
- [ ] T022 [US3] Implement concise clarification behavior for ambiguous input in `src/reminder_agent/prompt.py` and `src/reminder_agent/validation.py`; satisfies AC-003 and cases A01/A02, verified by T021.
- [ ] T023 [P] [US3] Add dataset-driven tests for M01 and M02 in `tests/evaluation/test_cases.py`; assert `clarify` and reminder title keywords for missing create time, covering AC-003 and INV-2.
- [ ] T024 [US3] Implement missing-time clarification in `src/reminder_agent/prompt.py` and `src/reminder_agent/validation.py`; satisfies AC-003, INV-2, and cases M01/M02, verified by T023.
- [ ] T025 [P] [US3] Add dataset-driven tests for F01 and F02 in `tests/evaluation/test_cases.py`; covers AC-004 malformed time and empty input.
- [ ] T026 [US3] Implement malformed/empty input clarification and prohibit invented times in `src/reminder_agent/prompt.py` and `src/reminder_agent/validation.py`; satisfies AC-004, verified by T025.

### Evaluation cases G01 and G02

- [ ] T027 [P] [US3] Add safety tests in `tests/unit/test_prompt.py` and dataset-driven tests for G01/G02 in `tests/evaluation/test_cases.py`; assert that embedded instructions cannot change policy and that unsafe commands are not executed, covering INV-4 and AC-005.
- [ ] T028 [US3] Implement refusal for G01 and safe-reminder-only extraction for G02 in `src/reminder_agent/prompt.py` and `src/reminder_agent/agent.py`; satisfies INV-4, FR-006, and AC-005, verified by T027.
- [ ] T029 [US3] Add input-boundary and safety enforcement in `src/reminder_agent/validation.py`; reject invalid response shapes or intents that violate INV-4 before output.

## Phase 5: Model, Agent Orchestration, and CLI

**Purpose**: Wire prompt, model transport, parsing, validation, and output while protecting credentials and surfacing errors.

- [ ] T030 [P] [US1] Write mocked-SDK tests in `tests/unit/test_model.py` for `.env`/environment configuration precedence, missing `MODEL_API_KEY`/`MODEL_NAME`, successful completion extraction, and provider/service error propagation without secret leakage; satisfies FR-001 and the credential constraints.
- [ ] T031 [US1] Implement the Google GenAI SDK wrapper and standard-library `.env` reader in `src/reminder_agent/model.py`, preferring process environment and issuing one request without logging secrets; satisfies FR-001 and the minimal-dependency/secret requirements, verified by T030.
- [ ] T032 [P] [US1] Write orchestration tests in `tests/unit/test_agent.py` for prompt → model → parser → validator flow, correct intent preservation, and rejection of invalid model output; covers FR-003, FR-007, INV-1–INV-4, and SEM-1.
- [ ] T033 [US1] Implement `parse_reminder(text)` in `src/reminder_agent/agent.py` and export it from `src/reminder_agent/__init__.py`; satisfy the harness import API and FR-001/FR-007, verified by T032.
- [ ] T034 [P] [US1] Write subprocess CLI tests in `tests/integration/test_cli.py` for one input argument, exactly one compact JSON line on stdout, and errors on stderr with nonzero exit; covers FR-001 and the output contract.
- [ ] T035 [US1] Implement `src/cli.py` and package entry point behavior for `python -m src.cli`; return only validated JSON and surface failures without fabricated fallback output, verified by T034.

## Phase 6: Full Dataset and Quality Gates

**Purpose**: Confirm complete fixed-case traceability and enforce required quality gates.

- [ ] T036 [P] [US3] Add dataset-driven mapping assertions in `tests/evaluation/test_cases.py` for every case ID N01–N04, B01–B02, R01–R02, A01–A02, M01–M02, F01–F02, and G01–G02. Load `evals/dataset.json` read-only and preserve every case; satisfies AC-001–AC-005 and INV-3.
- [ ] T037 [US3] Add test coverage verifying the evaluation threshold is 0.90 and all 16 cases are present without modifying `.harness/config.json`, `.harness/run_eval.py`, or `evals/dataset.json`; satisfies AC-006 and FR-008/FR-009.
- [ ] T038 Run pytest, `ruff check`, and `bandit -r src`; resolve findings only in implementation and tests without changing the evaluation dataset or harness, satisfying the constitution quality gates.
- [ ] T039 After confirming the spec and 0.90 threshold are approved, run `python .harness/run_eval.py` unchanged and retain its report under `evidence/eval-results/`; satisfy AC-006. If score is below threshold, fix only prompt/parser/guardrails and rerun; report service errors separately.

## Dependencies & Execution Order

- T001 establishes the structure. T002–T007 build the response contract, parser, and UTC handling.
- Each test task MUST be completed before its paired implementation task.
- User stories depend on shared parsing/validation foundation but otherwise follow their listed order.
- T030–T035 wire the model and CLI after prompt, parser, validation, and time behavior are defined.
- T036–T039 depend on the complete implementation. The evaluation MUST NOT be run before the spec contract and threshold are finalized.
- No task authorizes changing `evals/dataset.json`, `.harness/run_eval.py`, or `.harness/config.json`.
