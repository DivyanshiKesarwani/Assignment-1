"""Strict JSON decoding for untrusted model responses."""

import json
from typing import Any

from src.reminder_agent.errors import ResponseParseError


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ResponseParseError("Model response contains a duplicate JSON key")
        result[key] = value
    return result


def parse_json_response(raw: str) -> dict[str, Any]:
    """Parse exactly one JSON object, rejecting ambiguous representations."""
    if not isinstance(raw, str) or not raw.strip():
        raise ResponseParseError("Model response is empty")
    try:
        result = json.loads(raw, object_pairs_hook=_unique_object)
    except ResponseParseError:
        raise
    except (json.JSONDecodeError, TypeError, ValueError):
        raise ResponseParseError("Model response is not valid standalone JSON") from None
    if not isinstance(result, dict):
        raise ResponseParseError("Model response must be one JSON object")
    return result
