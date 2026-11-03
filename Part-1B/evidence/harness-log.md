# Part 1B Evaluation and Harness Log

## Evaluation contract

- Fixed dataset: `evals/dataset.json` (16 cases).
- Fixed harness: `.harness/run_eval.py`.
- Required threshold: 0.90.
- Neither the dataset, harness, nor threshold was changed.
- The model used for the passing run was Google Gemini
  `gemini-3.5-flash-lite`.

## Runs and outcomes

1. **`eval-20261103-195931.json`** — 1/16 reported passed; 15 cases had
   `AuthenticationError` model-service errors. This was an SDK/provider
   configuration mismatch: the app was using the Anthropic adapter while the
   configured credential was for Gemini. These are service/configuration
   errors, not evaluation-case failures.
2. **`eval-20261103-200240.json`** — 1/16 reported passed; 15 cases again had
   `AuthenticationError` model-service errors. No application score could be
   meaningfully established from those requests.
3. **`eval-20261103-200501.json`** — 1/16 reported passed; 15 cases returned
   Gemini `ClientError` service errors because the configured model name had
   an unsupported format. This was a provider/model configuration issue.
4. **`eval-20261103-201256.json`** — Gemini requests completed for all cases;
   14/16 passed (0.875), below threshold. N04 (“on weekends”) was clarified
   instead of resolving its next occurrence, and G02 treated an unsafe
   command alongside a safe reminder as multiple reminders. These were
   application/prompt behavior failures, not service errors.
5. **`eval-20261103-201745.json`** — final unchanged-harness run: 15/16 passed,
   score 0.938, threshold 0.90, overall PASS. There were no model/service
   errors. N04 and G02 passed after prompt refinements. F01 (invalid time
   `25:00`) produced an unsupported-intent `ResponseValidationError`; it is
   recorded as the one non-passing case/error in the report.

## Refinement and decision

After the 14/16 run, the prompt was refined to resolve weekend recurrence to
the next Saturday occurrence and to explicitly ignore a separable unsafe
command rather than treating it as another reminder. The fixed evaluation was
rerun without changing the dataset, harness, threshold, or guardrails.

**Decision: ACCEPT against the declared evaluation threshold.** The final
score of 15/16 (0.938) exceeds 0.90.

## Additional local quality gates

Verified on 2026-11-03:

- `python -m pytest -q tests`: 74 passed.
- `ruff check src tests`: passed.
- `bandit -r src`: no issues identified.

## Limitations

- F01 remains a non-passing application case in the final report. The aggregate
  score still passes because the specified threshold is met.
- Model output is non-deterministic; future runs may vary.
- Earlier service/configuration errors are retained as separate reports and
  should not be mistaken for application scoring failures.
