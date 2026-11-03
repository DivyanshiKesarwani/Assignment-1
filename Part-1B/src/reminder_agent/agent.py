"""Public orchestration entry point for reminder interpretation."""

from src.reminder_agent.model import generate_response
from src.reminder_agent.parser import parse_json_response
from src.reminder_agent.prompt import build_messages
from src.reminder_agent.time_utils import capture_reference_time
from src.reminder_agent.validation import is_primary_unsafe_request, validate_response


def parse_reminder(text: str) -> dict[str, str | None]:
    """Interpret one user sentence and return only independently validated data."""
    if not isinstance(text, str):
        raise TypeError("reminder input must be a string")
    if is_primary_unsafe_request(text):
        return validate_response(
            {
                "intent": "refuse",
                "title": None,
                "due_datetime": None,
                "clarification_question": None,
            }
        )
    reference_time = capture_reference_time()
    system_prompt, user_message = build_messages(text, reference_time)
    raw_response = generate_response(system_prompt, user_message)
    parsed_response = parse_json_response(raw_response)
    return validate_response(parsed_response, reference_time)
