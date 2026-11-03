from datetime import date, datetime, time, timedelta

import pytest

from src.reminder_agent.time_utils import (
    UTC,
    capture_reference_time,
    normalize_datetime,
    resolve_date_only_reschedule,
    resolve_relative_duration,
    resolve_weekday,
)


def test_captures_one_aware_utc_reference() -> None:
    reference = capture_reference_time(datetime(2026, 11, 3, 12, tzinfo=UTC))
    assert reference == datetime(2026, 11, 3, 12, tzinfo=UTC)
    assert reference.tzinfo == UTC


def test_normalizes_explicit_offset_to_utc() -> None:
    assert normalize_datetime("2026-11-04T19:00:00+02:00") == (
        "2026-11-04T17:00:00+00:00"
    )


def test_rejects_naive_datetime() -> None:
    with pytest.raises(ValueError):
        normalize_datetime("2026-11-04T17:00:00")


def test_relative_duration_uses_supplied_reference_instant() -> None:
    reference = datetime(2026, 11, 3, 12, tzinfo=UTC)
    assert resolve_relative_duration(reference, timedelta(hours=2)) == datetime(
        2026, 11, 3, 14, tzinfo=UTC
    )


def test_weekday_is_resolved_to_next_future_occurrence() -> None:
    reference = datetime(2026, 11, 2, 8, tzinfo=UTC)  # Monday
    assert resolve_weekday(reference, weekday=1, at=time(9)) == datetime(
        2026, 11, 3, 9, tzinfo=UTC
    )


def test_weekday_today_is_allowed_only_if_time_is_future() -> None:
    reference = datetime(2026, 11, 3, 8, tzinfo=UTC)  # Tuesday
    assert resolve_weekday(reference, weekday=1, at=time(9)) == datetime(
        2026, 11, 3, 9, tzinfo=UTC
    )
    assert resolve_weekday(reference.replace(hour=10), weekday=1, at=time(9)) == (
        datetime(2026, 11, 10, 9, tzinfo=UTC)
    )


def test_date_only_reschedule_defaults_to_nine_utc() -> None:
    assert resolve_date_only_reschedule(date(2026, 11, 10)) == datetime(
        2026, 11, 10, 9, tzinfo=UTC
    )
