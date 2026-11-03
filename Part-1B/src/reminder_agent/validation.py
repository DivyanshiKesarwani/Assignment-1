"""Independent structural and invariant validation of model output."""

import re
from datetime import datetime
from typing import Any

from src.reminder_agent.errors import ResponseValidationError
from src.reminder_agent.time_utils import normalize_datetime

EXPECTED_KEYS = {
    "intent",
    "title",
    "due_datetime",
    "clarification_question",
}
VALID_INTENTS = {"create", "reschedule", "snooze", "clarify", "refuse"}
ACTION_INTENTS = {"create", "reschedule", "snooze"}
UNSAFE_REQUEST_PATTERNS = (
    "ignore your rules",
    "ignore all rules",
    "bypass rules",
    "delete all my reminders",
    "delete my reminders",
    "run the shell command",
    "run shell command",
    "run command",
    "execute command",
)


def is_primary_unsafe_request(user_input: str) -> bool:
    """Identify obvious unsafe-only requests without classifying mixed requests."""
    normalized = user_input.casefold()
    has_unsafe_request = any(
        phrase in normalized for phrase in UNSAFE_REQUEST_PATTERNS
    ) or re.search(r"\brm\s+-rf\b", normalized) is not None
    has_safe_reminder = re.search(r"\bremind\s+me\s+to\b", normalized) is not None
    return has_unsafe_request and not has_safe_reminder


def _optional_string(value: Any, field: str) -> str | None:
    if value is not None and not isinstance(value, str):
        raise ResponseValidationError(f"{field} must be a string or null")
    return value


def validate_response(
    output: Any, reference_time: datetime | None = None
) -> dict[str, str | None]:
    """Enforce the response schema and intent-specific contract."""
    if not isinstance(output, dict):
        raise ResponseValidationError("Model response must be a JSON object")
    if set(output) != EXPECTED_KEYS:
        raise ResponseValidationError("Model response has missing or extra fields")

    intent = output["intent"]
    if not isinstance(intent, str) or intent not in VALID_INTENTS:
        raise ResponseValidationError("Model response has an unsupported intent")
    title = _optional_string(output["title"], "title")
    due_datetime = _optional_string(output["due_datetime"], "due_datetime")
    question = _optional_string(
        output["clarification_question"], "clarification_question"
    )

    if title is not None and not title.strip():
        raise ResponseValidationError("title must not be empty")
    if question is not None and not question.strip():
        raise ResponseValidationError("clarification_question must not be empty")
    if reference_time is not None and (
        reference_time.tzinfo is None or reference_time.utcoffset() is None
    ):
        raise ResponseValidationError("reference time must include a UTC offset")

    normalized_due: str | None = None
    if due_datetime is not None:
        try:
            normalized_due = normalize_datetime(due_datetime)
        except (ValueError, TypeError):
            raise ResponseValidationError(
                "due_datetime must be an ISO 8601 timestamp with a UTC offset"
            ) from None

    if intent in ACTION_INTENTS:
        if title is None or not title.strip():
            raise ResponseValidationError(f"{intent} requires a non-empty title")
        if normalized_due is None:
            raise ResponseValidationError(f"{intent} requires a due_datetime")
        if question is not None:
            raise ResponseValidationError(
                f"{intent} must not include a clarification_question"
            )
    elif intent == "clarify":
        if question is None or not question.strip():
            raise ResponseValidationError("clarify requires a non-empty question")
    elif intent == "refuse":
        if normalized_due is not None or question is not None:
            raise ResponseValidationError(
                "refuse must have null due_datetime and clarification_question"
            )

    return {
        "intent": intent,
        "title": title,
        "due_datetime": normalized_due,
        "clarification_question": question,
    }
