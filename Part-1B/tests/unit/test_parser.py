import pytest

from src.reminder_agent.parser import ResponseParseError, parse_json_response


def test_parses_one_json_object() -> None:
    assert parse_json_response('{"intent":"create"}') == {"intent": "create"}


@pytest.mark.parametrize(
    "raw",
    [
        "",
        "```json\n{}\n```",
        '{"intent":',
        "[]",
        '{"a":1} trailing',
        '{"intent":"create","intent":"refuse"}',
    ],
)
def test_rejects_malformed_or_ambiguous_json(raw: str) -> None:
    with pytest.raises(ResponseParseError):
        parse_json_response(raw)
