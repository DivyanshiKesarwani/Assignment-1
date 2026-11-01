# Spec Kit prompts for Part 1B

Paste these into your agent one at a time, in order. Save each output.

## /speckit.constitution
Project: Natural-Language Reminder Agent (Python 3.11+).
- Non-deterministic LLM output must be validated by an independent harness, never trusted directly.
- Output schema, invariants, guardrails and the pass threshold must be defined in the spec before any evaluation run.
- Harness must not be weakened, and no eval case may be removed to pass.
- Secrets/API keys only via a local .env; never committed.
- Dependencies: standard library plus the chosen model SDK, pytest, ruff, bandit.

## /speckit.specify
Build a CLI that takes one natural-language sentence and returns a JSON object with fields:
intent (one of create, reschedule, snooze, clarify, refuse), title (string or null), due_datetime (ISO 8601 string or null), clarification_question (string or null).
Behaviour: create/reschedule/snooze extract the reminder; if no time is given for create, ask a clarification question; malformed or empty input yields clarify; requests to bypass rules or run commands yield refuse or ignore the unsafe part.
Specify: output schema contract, structural invariants INV-1 to INV-4, semantic check SEM-1, and an evaluation threshold of 0.90 (score = passed cases / total).
Acceptance criteria must map to the eval cases in evals/dataset.json.

## /speckit.clarify
List ambiguities (time zone handling, relative times like "in 2 hours", recurring reminders, multiple reminders in one sentence). Propose one answer for each and record it in the spec.

## /speckit.plan
Plan the agent: prompt construction, model call wrapper, JSON parsing, and the module layout under src/. Map each invariant and eval case to the module that handles it.

## /speckit.tasks
Break the plan into small ordered tasks. Each task names the spec requirement or eval case it satisfies.

## /speckit.analyze
Check spec, plan and tasks for consistency. Report any eval case or invariant with no task, and any task with no requirement.

## /speckit.implement
Implement approved tasks only. Do not edit evals/dataset.json, .harness/, the threshold, or the guardrails to get PASS. If the harness fails, report the failing case and fix the agent (prompt, parser or guardrail). Record model/service errors separately from application failures.
