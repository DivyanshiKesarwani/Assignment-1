# Natural-Language Reminder Agent Constitution

## Core Principles

### I. Independently Validated Model Output
Model output is non-deterministic and MUST be treated as untrusted input. Every response MUST be parsed and validated by an independent harness before it is accepted or returned as application output. The harness MUST enforce the contract defined in the specification; prompt instructions alone are not validation.

### II. Contract Before Evaluation
Before any evaluation run, the specification MUST define the output schema, structural invariants, semantic checks, safety guardrails, evaluation cases, and pass threshold. These requirements MUST be explicit and objectively testable.

### III. Immutable Evaluation Integrity
The evaluation harness and evaluation dataset MUST NOT be weakened, bypassed, or altered to obtain a passing result. Evaluation cases MUST NOT be removed or skipped. Failures MUST be addressed in the application, prompt, parser, or guardrails while preserving the approved evaluation contract.

### IV. Secret and Credential Protection
API keys and other secrets MUST be supplied only through a local `.env` file. `.env` MUST NOT be committed, and secrets MUST NOT be included in source code, prompts, tests, logs, evaluation output, or other committed files.

### V. Minimal, Approved Dependencies
The project targets Python 3.11 or later. Runtime dependencies are limited to the Python standard library and the selected model SDK. `pytest`, `ruff`, and `bandit` are development-only tools.

## Technical Constraints

- The application MUST validate model responses against the specification before using or returning them.
- The evaluation threshold, schema, invariants, guardrails, and test cases MUST be established in the spec before evaluation.
- The harness and dataset are fixed quality gates; passing them MUST NOT be achieved by reducing coverage or changing their expected behavior.
- Secrets are local-only and MUST be excluded from version control.
- Runtime dependencies MUST be limited to Python 3.11+ standard library modules and the selected model SDK.

## Development Workflow

- Write and review the complete output contract and evaluation requirements before running the evaluation.
- Keep each invariant and evaluation case traceable to tests and implementation tasks.
- Run the independent evaluation harness without modifying it or removing cases.
- When results fail, report the failing cases and fix the prompt, parser, or guardrails without weakening the evaluation.
- Record model/service failures separately from application failures.
- Run pytest, `ruff check`, and `bandit -r src` as development quality checks.
- Verify that `.env` and all credentials are absent from staged and committed changes.

## Governance

This constitution governs the specification, plan, tasks, implementation, prompts, parser, guardrails, and evaluation process. Changes to these principles MUST be explicit and documented. If a proposed change would weaken the harness, remove evaluation coverage, or expose a secret, it MUST NOT be made.

**Version**: 1.0.0 | **Ratified**: 2026-11-03 | **Last Amended**: 2026-11-03
