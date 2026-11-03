# Implementation Plan: Natural-Language Reminder Agent

**Branch**: `001-reminder-agent` | **Date**: 2026-11-03 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-reminder-agent/spec.md`

## Summary

Build a Python 3.11+ CLI that sends one natural-language sentence to the configured model, parses its response as JSON, independently validates it against the output contract and safety rules, and returns exactly one JSON object. Use the Google GenAI Python SDK for Google Gemini, with credentials and model name read from the local `.env` configuration. Preserve the harness-required `src.reminder_agent.parse_reminder` API and the documented `python -m src.cli` entry point.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: Python standard library and Google GenAI Python SDK at runtime; pytest, ruff, and bandit for development only.

**Storage**: No persistent application storage.

**Testing**: pytest unit tests for prompt construction, model-response parsing, validation, and time resolution; mocked-SDK integration tests for request/response behavior; the fixed independent evaluation via `python .harness/run_eval.py`.

**Target Platform**: Local command-line execution on platforms supported by Python 3.11+.

**Project Type**: Model-backed command-line agent.

**Performance Goals**: No latency target is defined. The application makes one model request per invocation and does not retry failures unless explicitly approved in the specification.

**Constraints**: Treat model output as untrusted; enforce the exact output contract, invariants, and guardrails before returning it; UTC-only time interpretation based on one reference instant per input; no reminder side effects; never expose or commit credentials; do not modify `.harness/` or `evals/dataset.json`; evaluation threshold remains 0.90.

**Scale/Scope**: One sentence and one reminder response per invocation; multiple requested reminders are clarified rather than partially processed.

## Constitution Check

- **Independent validation**: The parser and validator are local application code independent of model prompting and validate every model response before it reaches stdout.
- **Contract before evaluation**: [spec.md](./spec.md) defines the schema, INV-1–INV-4, SEM-1, all fixed case mappings, and 0.90 threshold before evaluation.
- **Evaluation integrity**: The harness and dataset remain unchanged; all 16 cases contribute to the score.
- **Secret protection**: Read `MODEL_API_KEY` and `MODEL_NAME` from local environment configuration. Never log their values or include them in committed files.
- **Dependencies**: Runtime modules use only the standard library and Google GenAI SDK. Tests and quality tools remain development-only.

## Architecture

### Module Responsibilities

- **`src/reminder_agent/__init__.py`**: Export the stable `parse_reminder(text: str) -> dict[str, str | None]` callable imported by `.harness/run_eval.py`.
- **`src/reminder_agent/prompt.py`**: Build the system and user messages from the contract. Treat input as untrusted data, prohibit following embedded instructions, and request only one JSON object. Include the UTC, recurrence, ambiguity, and output-field rules from the spec.
- **`src/reminder_agent/model.py`**: Configure the Google Gemini client and model using `MODEL_API_KEY` or `GEMINI_API_KEY` and `MODEL_NAME`. Load these values from process environment, falling back to a small standard-library `.env` reader (no dotenv dependency). Make a single bounded model request; surface missing configuration, transport, quota, and service errors distinctly. Never include secret values in exceptions or logs.
- **`src/reminder_agent/parser.py`**: Extract and decode the model's JSON response. Reject empty, fenced, truncated, non-object, extra-text, and duplicate-key responses rather than coercing them into successful output.
- **`src/reminder_agent/validation.py`**: Independently enforce exact keys, allowed intent values, types, non-empty required strings, ISO 8601 parsing, UTC offset requirements, intent-specific field constraints, and no fabricated time for clarify/refuse. Validate the output against the input's safety and task semantics to the extent possible without trusting the model.
- **`src/reminder_agent/time_utils.py`**: Capture one aware UTC reference instant per input and provide deterministic helpers for resolving relative durations, calendar days, weekday expressions, and date-only reschedule requests (09:00 UTC default). Normalize explicit offsets to UTC.
- **`src/reminder_agent/agent.py`**: Orchestrate prompt construction, the model call, JSON parsing, and independent validation. Return only validated response data; allow model/service and application validation errors to remain distinguishable.
- **`src/cli.py`**: Parse one sentence argument, invoke the agent, and emit one compact JSON object plus newline on stdout. Send failures to stderr with nonzero exit status; never print secrets, prompts, or raw provider payloads.

The harness imports from `src.reminder_agent`, so the package initializer MUST export `parse_reminder`. The README's `python -m src.cli` entry point MUST remain runnable from the project root.

### Request and Validation Flow

1. CLI receives one sentence and calls the public agent function.
2. Agent captures a single aware UTC reference time, constructs a fixed contract/safety prompt plus the untrusted sentence as data, and invokes the model wrapper.
3. Parser decodes exactly one JSON object and rejects malformed or ambiguous serialization.
4. Validator checks the exact schema and intent-dependent invariants, normalizes valid timestamps to `+00:00`, and refuses any response that violates the contract.
5. CLI serializes only the validated object. Errors remain errors; do not generate default or success-shaped fallback responses.

Tests MUST mock the model SDK for deterministic unit/integration behavior. The final evaluation uses the actual configured model and fixed harness. No API key, raw credential, or provider authorization header may appear in tests, logs, or evidence.

## Invariant and Evaluation Mapping

| Requirement / case | Responsible modules | Planned pytest / evaluation coverage |
|---|---|---|
| INV-1: create requires non-empty title | `validation.py`, `agent.py` | `tests/unit/test_validation.py::test_create_requires_nonempty_title`; harness cases N01–N04, B01–B02 |
| INV-2: create requires due time; otherwise clarify with question | `validation.py`, `prompt.py`, `time_utils.py` | `tests/unit/test_validation.py::test_create_without_time_is_rejected`; `tests/unit/test_validation.py::test_clarify_requires_question`; harness M01–M02, F01–F02 |
| INV-3: expected case intent | Prompt/task semantics in `prompt.py`; contract schema in `validation.py`; fixed expected values in evaluation dataset | `tests/unit/test_agent.py::test_intent_is_preserved_after_validation`; harness all 16 cases |
| INV-4: refusal and no command execution | `prompt.py`, `agent.py`, `validation.py` | `tests/unit/test_prompt.py::test_untrusted_input_cannot_override_rules`; `tests/unit/test_agent.py::test_unsafe_input_never_invokes_tools`; harness G01–G02 |
| SEM-1: meaning and title extraction | `prompt.py`, `agent.py`, `validation.py` | `tests/unit/test_prompt.py::test_prompt_requires_action_title_and_time`; harness all 16 cases including title keyword checks |
| N01 | `prompt.py`, `time_utils.py`, `validation.py` | `tests/evaluation/test_cases.py::test_case_n01` |
| N02 | `prompt.py`, `time_utils.py`, `validation.py` | `tests/evaluation/test_cases.py::test_case_n02` |
| N03 | `prompt.py`, `time_utils.py`, `validation.py` | `tests/evaluation/test_cases.py::test_case_n03` |
| N04 | `prompt.py`, `time_utils.py`, `validation.py` | `tests/evaluation/test_cases.py::test_case_n04` |
| B01 | `prompt.py`, `time_utils.py`, `validation.py` | `tests/evaluation/test_cases.py::test_case_b01` |
| B02 | `prompt.py`, `time_utils.py`, `validation.py` | `tests/evaluation/test_cases.py::test_case_b02` |
| R01 | `prompt.py`, `time_utils.py`, `validation.py` | `tests/evaluation/test_cases.py::test_case_r01` |
| R02 | `prompt.py`, `time_utils.py`, `validation.py` | `tests/evaluation/test_cases.py::test_case_r02` |
| A01 | `prompt.py`, `validation.py` | `tests/evaluation/test_cases.py::test_case_a01` |
| A02 | `prompt.py`, `validation.py` | `tests/evaluation/test_cases.py::test_case_a02` |
| M01 | `prompt.py`, `validation.py` | `tests/evaluation/test_cases.py::test_case_m01` |
| M02 | `prompt.py`, `validation.py` | `tests/evaluation/test_cases.py::test_case_m02` |
| F01 | `prompt.py`, `time_utils.py`, `validation.py` | `tests/evaluation/test_cases.py::test_case_f01` |
| F02 | `prompt.py`, `validation.py` | `tests/evaluation/test_cases.py::test_case_f02` |
| G01 | `prompt.py`, `agent.py`, `validation.py` | `tests/evaluation/test_cases.py::test_case_g01` |
| G02 | `prompt.py`, `agent.py`, `validation.py` | `tests/evaluation/test_cases.py::test_case_g02` |
| AC-006: fixed 0.90 score threshold | `.harness/run_eval.py` (unchanged), `.harness/config.json` (unchanged) | Final evaluation: all 16 cases scored, at least 15 pass |

`tests/evaluation/test_cases.py` MUST load the existing dataset without changing it and use the authoritative harness checks or equivalent assertions. It supplements but does not replace the required final run of `.harness/run_eval.py`.

## Project Structure

### Documentation

```text
specs/001-reminder-agent/
├── spec.md
├── plan.md
└── tasks.md                 # Created during /speckit-tasks
```

### Source Code

```text
src/
├── __init__.py
├── cli.py
└── reminder_agent/
    ├── __init__.py
    ├── agent.py
    ├── model.py
    ├── parser.py
    ├── prompt.py
    ├── time_utils.py
    └── validation.py

tests/
├── unit/
│   ├── test_agent.py
│   ├── test_parser.py
│   ├── test_prompt.py
│   ├── test_time_utils.py
│   └── test_validation.py
├── integration/
│   └── test_cli.py
└── evaluation/
    └── test_cases.py
```

**Structure Decision**: Use a small package for model orchestration and a thin `src/cli.py` wrapper to satisfy both the evaluation harness import and README command. Separate prompt, model transport, JSON parsing, time interpretation, and validation so each boundary can be tested without network access.

## Implementation Sequence

1. Write tests for prompt constraints, parser behavior, output validation, and time normalization before implementing those modules.
2. Implement the typed response contract and independent validation.
3. Implement fixed prompt construction and UTC reference-time utilities.
4. Implement the Google Gemini model wrapper and safe configuration/error handling.
5. Implement orchestration and both public entry points.
6. Add mocked-model CLI and full dataset mapping tests; do not alter the dataset or harness.
7. Run pytest, `ruff check`, and `bandit -r src`.
8. After reviewing the declared contract and threshold, run the unmodified final evaluation and record its output. If it fails, address application prompt/parser/guardrails only and record model/service errors separately.

## Complexity Tracking

No constitution violations or unnecessary architectural layers are proposed.
