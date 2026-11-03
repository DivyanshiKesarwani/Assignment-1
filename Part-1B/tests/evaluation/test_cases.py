import json
from pathlib import Path

import pytest

from src.reminder_agent.prompt import build_messages
from src.reminder_agent.validation import validate_response

ROOT = Path(__file__).resolve().parents[2]
DATASET = json.loads((ROOT / "evals" / "dataset.json").read_text(encoding="utf-8"))
EXPECTED_CASE_IDS = {
    "N01", "N02", "N03", "N04", "B01", "B02", "R01", "R02",
    "A01", "A02", "M01", "M02", "F01", "F02", "G01", "G02",
}


def test_dataset_contains_all_specified_cases() -> None:
    assert {case["id"] for case in DATASET["cases"]} == EXPECTED_CASE_IDS


@pytest.mark.parametrize("case", DATASET["cases"], ids=lambda case: case["id"])
def test_case_prompt_keeps_dataset_input_as_untrusted_user_data(case) -> None:
    system, user = build_messages(case["input"])

    assert json.dumps(case["input"], ensure_ascii=False) in user
    if case["input"]:
        assert case["input"] not in system
    assert "untrusted" in system.lower()
    assert case["input"] in user


@pytest.mark.parametrize("case", DATASET["cases"], ids=lambda case: case["id"])
def test_case_fixture_response_satisfies_response_contract(case) -> None:
    intent = case["expected_intent"]
    title = " ".join(case["title_keywords"]) or None
    if intent == "clarify":
        due = None
        question = "What time or reminder details should I use?"
    elif intent == "refuse":
        due = None
        question = None
    else:
        due = "2026-11-10T09:00:00+00:00"
        question = None
    output = {
        "intent": intent,
        "title": title,
        "due_datetime": due,
        "clarification_question": question,
    }

    validated = validate_response(output)

    assert validated["intent"] == case["expected_intent"]
    normalized_title = (validated["title"] or "").lower()
    assert all(keyword.lower() in normalized_title for keyword in case["title_keywords"])


def test_spec_threshold_maps_to_at_least_fifteen_cases() -> None:
    config = json.loads((ROOT / ".harness" / "config.json").read_text(encoding="utf-8"))
    assert config["pass_threshold"] == 0.90
    assert len(DATASET["cases"]) == 16
    assert int(config["pass_threshold"] * len(DATASET["cases"])) + 1 == 15
