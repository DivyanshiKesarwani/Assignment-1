"""Deterministic UTC time helpers shared by prompts and validation."""

from datetime import UTC, date, datetime, time, timedelta


def _require_aware(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("datetime must include a UTC offset")
    return value.astimezone(UTC)


def capture_reference_time(now: datetime | None = None) -> datetime:
    """Capture or normalize the one UTC reference instant for a request."""
    return _require_aware(now if now is not None else datetime.now(UTC))


def normalize_datetime(value: str) -> str:
    """Validate an ISO 8601 timestamp and return it in UTC."""
    parsed = datetime.fromisoformat(value)
    return _require_aware(parsed).isoformat()


def resolve_relative_duration(
    reference_time: datetime, duration: timedelta
) -> datetime:
    reference = _require_aware(reference_time)
    if duration <= timedelta(0):
        raise ValueError("duration must be positive")
    return reference + duration


def resolve_weekday(
    reference_time: datetime, weekday: int, at: time
) -> datetime:
    """Resolve weekday (Monday=0) at a UTC clock time to its next occurrence."""
    reference = _require_aware(reference_time)
    if weekday < 0 or weekday > 6:
        raise ValueError("weekday must be between 0 and 6")
    if at.tzinfo is not None:
        raise ValueError("clock time must not include a timezone")
    days_ahead = (weekday - reference.weekday()) % 7
    candidate_date = reference.date() + timedelta(days=days_ahead)
    candidate = datetime.combine(candidate_date, at, tzinfo=UTC)
    if candidate <= reference:
        candidate += timedelta(days=7)
    return candidate


def resolve_date_only_reschedule(day: date) -> datetime:
    """Resolve a date-only reschedule to 09:00 UTC on that date."""
    return datetime.combine(day, time(9), tzinfo=UTC)
