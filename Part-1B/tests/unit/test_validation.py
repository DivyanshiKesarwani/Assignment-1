from datetime import UTC, datetime

import pytest

from src.reminder_agent.validation import (
    ResponseValidationError,
    validate_response,
)


def response(**overrides):
    value = {
        "intent": "create",
        "title": "Call mom",
        "due_datetime": "2026-11-04T17:00:00+00:00",
        "clarification_question": None,
    }
    value.update(overrides)
    return value


def test_accepts_and_normalizes_iso_datetime_to_utc() -> None:
    result = validate_response(
        response(due_datetime="2026-11-04T19:00:00+02:00"),
        datetime(2026, 11, 3, tzinfo=UTC),
    )

    assert result["due_datetime"] == "2026-11-04T17:00:00+00:00"


def test_rejects_missing_or_extra_fields() -> None:
    with pytest.raises(ResponseValidationError):
        validate_response({"intent": "create"}, datetime.now(UTC))
    with pytest.raises(ResponseValidationError):
        validate_response(
            {**response(), "extra": True}, datetime.now(UTC)
        )


def test_rejects_invalid_intent_and_field_types() -> None:
    with pytest.raises(ResponseValidationError):
        validate_response(response(intent="delete"), datetime.now(UTC))
    with pytest.raises(ResponseValidationError):
        validate_response(response(title=7), datetime.now(UTC))


def test_create_requires_nonempty_title() -> None:
    with pytest.raises(ResponseValidationError):
        validate_response(response(title="  "), datetime.now(UTC))


def test_create_requires_due_time() -> None:
    with pytest.raises(ResponseValidationError):
        validate_response(response(due_datetime=None), datetime.now(UTC))


def test_clarify_requires_question() -> None:
    valid = response(
        intent="clarify",
        title="Buy groceries",
        due_datetime=None,
        clarification_question="What time should I remind you?",
    )
    assert validate_response(valid, datetime.now(UTC)) == valid

    with pytest.raises(ResponseValidationError):
        validate_response(
            {**valid, "clarification_question": None}, datetime.now(UTC)
        )


@pytest.mark.parametrize("intent", ["reschedule", "snooze"])
def test_reschedule_and_snooze_require_title_and_due_time(intent: str) -> None:
    valid = response(intent=intent)
    assert validate_response(valid, datetime.now(UTC))["intent"] == intent

    with pytest.raises(ResponseValidationError):
        validate_response(
            {**valid, "due_datetime": None}, datetime.now(UTC)
        )


def test_refuse_has_no_due_time_or_question() -> None:
    valid = response(
        intent="refuse",
        title=None,
        due_datetime=None,
        clarification_question=None,
    )
    assert validate_response(valid, datetime.now(UTC)) == valid
    with pytest.raises(ResponseValidationError):
        validate_response(
            {**valid, "clarification_question": "Why?"}, datetime.now(UTC)
        )


def test_due_datetime_requires_aware_iso_datetime() -> None:
    with pytest.raises(ResponseValidationError):
        validate_response(
            response(due_datetime="2026-11-04T17:00:00"),
            datetime.now(UTC),
        )
