import pytest

from todo_cli.validation import ValidationError, validate_priority, validate_title


@pytest.mark.parametrize("length", [1, 200])
def test_title_length_boundaries(length: int) -> None:
    title = "x" * length

    assert validate_title(title) == title


@pytest.mark.parametrize("title", ["", " ", "\t\n", "x" * 201])
def test_rejects_blank_or_overlong_titles(title: str) -> None:
    with pytest.raises(ValidationError):
        validate_title(title)


def test_title_validation_preserves_original_text() -> None:
    title = "  Buy milk  "

    assert validate_title(title) == title


@pytest.mark.parametrize("priority", ["low", "medium", "high"])
def test_accepts_valid_priorities(priority: str) -> None:
    assert validate_priority(priority) == priority


@pytest.mark.parametrize("priority", ["urgent", "HIGH", ""])
def test_rejects_invalid_priority_values(priority: str) -> None:
    with pytest.raises(ValidationError):
        validate_priority(priority)


def test_omitted_priority_defaults_to_medium() -> None:
    assert validate_priority(None) == "medium"
