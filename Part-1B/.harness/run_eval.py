#!/usr/bin/env python3
"""Single non-deterministic evaluation harness for Part 1B.

Pipeline per case: agent output -> Layer 1 schema -> Layer 2 invariants/properties
-> Layer 3 semantic check -> aggregate against threshold in config.json.
Standard library only. The harness does not call the LLM itself (no LLM-as-judge here).
"""
import datetime
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

VALID_INTENTS = {"create", "reschedule", "snooze", "clarify", "refuse"}
REQUIRED_FIELDS = {"intent", "title", "due_datetime", "clarification_question"}


def load_agent():
    try:
        from src.reminder_agent import parse_reminder  # written by your coding agent
        return parse_reminder
    except ImportError as exc:
        sys.exit(f"Could not import src.reminder_agent.parse_reminder: {exc}")


# Layer 1: structural / schema validation
def check_schema(out):
    errors = []
    if not isinstance(out, dict):
        return ["output is not a JSON object"]
    missing = REQUIRED_FIELDS - out.keys()
    if missing:
        errors.append(f"missing fields: {sorted(missing)}")
    if out.get("intent") not in VALID_INTENTS:
        errors.append(f"intent not in {sorted(VALID_INTENTS)}: {out.get('intent')!r}")
    due = out.get("due_datetime")
    if due is not None:
        try:
            datetime.datetime.fromisoformat(due)
        except (TypeError, ValueError):
            errors.append(f"due_datetime is not ISO 8601: {due!r}")
    return errors


# Layer 2: property / invariant checks derived from the spec
def check_invariants(out, case):
    errors = []
    intent = out.get("intent")
    if intent == "create" and not out.get("title"):
        errors.append("INV-1: create intent requires a non-empty title")
    if out.get("due_datetime") is None and intent == "create" and not out.get("clarification_question"):
        errors.append("INV-2: create without a time must ask for clarification")
    if intent != case["expected_intent"]:
        errors.append(f"INV-3: intent {intent!r} != expected {case['expected_intent']!r}")
    if case["expected_intent"] == "refuse" and intent != "refuse":
        errors.append("INV-4 (guardrail): adversarial request was not refused")
    return errors


# Layer 3: semantic / quality check (task-specific heuristic, not LLM judging)
def check_semantic(out, case):
    errors = []
    title = (out.get("title") or "").lower()
    for kw in case.get("title_keywords", []):
        if kw.lower() not in title:
            errors.append(f"SEM-1: title {out.get('title')!r} missing keyword {kw!r}")
    return errors


def main():
    parse_reminder = load_agent()
    cfg = json.loads((ROOT / ".harness" / "config.json").read_text())
    cases = json.loads((ROOT / "evals" / "dataset.json").read_text())["cases"]

    results = []
    for case in cases:
        try:
            out = parse_reminder(case["input"])
        except Exception as exc:  # model/service failure, recorded separately from app failure
            results.append({"id": case["id"], "status": "ERROR", "error": repr(exc)})
            continue
        schema_errs = check_schema(out)
        inv_errs = check_invariants(out, case) if not schema_errs else []
        sem_errs = check_semantic(out, case) if not schema_errs else []
        all_errs = schema_errs + inv_errs + sem_errs
        results.append({
            "id": case["id"],
            "category": case["category"],
            "input": case["input"],
            "output": out,
            "status": "PASS" if not all_errs else "FAIL",
            "failures": all_errs,
        })

    scored = [r for r in results if r["status"] != "ERROR"]
    passed = sum(1 for r in scored if r["status"] == "PASS")
    score = passed / len(cases)
    overall = "PASS" if score >= cfg["pass_threshold"] else "FAIL"

    report = {
        "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        "total_cases": len(cases),
        "passed": passed,
        "errors_model_or_service": len(results) - len(scored),
        "score": round(score, 3),
        "threshold": cfg["pass_threshold"],
        "overall": overall,
        "results": results,
    }
    out_dir = ROOT / "evidence" / "eval-results"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"eval-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"Score {passed}/{len(cases)} = {score:.3f} (threshold {cfg['pass_threshold']}) -> {overall}")
    print(f"Report: {out.relative_to(ROOT)}")
    return 0 if overall == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
