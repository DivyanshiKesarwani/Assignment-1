from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def run_cli(
    tmp_path: Path,
    *arguments: str,
    data_path: Path | None = None,
    unset_data_path: bool = False,
) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(PROJECT_ROOT / "src")
    if unset_data_path:
        environment.pop("TODO_DATA_PATH", None)
    else:
        selected_path = data_path or tmp_path / "tasks.json"
        environment["TODO_DATA_PATH"] = str(selected_path)
    return subprocess.run(
        [sys.executable, "-m", "todo_cli", *arguments],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )


def load_tasks(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def add_task(
    tmp_path: Path,
    title: str,
    *options: str,
    data_path: Path | None = None,
) -> int:
    result = run_cli(tmp_path, "add", title, *options, data_path=data_path)
    assert result.returncode == 0, result.stderr
    assert re.fullmatch(r"[1-9]\d*\n", result.stdout)
    return int(result.stdout)


def test_add_returns_unique_positive_id_and_open_task(tmp_path: Path) -> None:
    storage_path = tmp_path / "tasks.json"
    first = add_task(tmp_path, "Buy milk", data_path=storage_path)
    second = add_task(tmp_path, "Walk dog", data_path=storage_path)

    data = load_tasks(storage_path)
    first_task = next(task for task in data["tasks"] if task["id"] == first)
    assert first > 0
    assert second > 0 and second != first
    assert first_task["title"] == "Buy milk"
    assert first_task["status"] == "open"


def test_deleted_task_id_is_not_reused(tmp_path: Path) -> None:
    first = add_task(tmp_path, "First")
    deleted = run_cli(tmp_path, "delete", str(first))
    assert deleted.returncode == 0, deleted.stderr

    second = add_task(tmp_path, "Second")

    assert second != first


def test_add_stores_tag_and_explicit_priority(tmp_path: Path) -> None:
    task_id = add_task(tmp_path, "Buy milk", "--tag", "Work", "--priority", "high")

    task = next(
        item
        for item in load_tasks(tmp_path / "tasks.json")["tasks"]
        if item["id"] == task_id
    )
    assert task["tag"] == "Work"
    assert task["priority"] == "high"


def test_add_defaults_priority_to_medium(tmp_path: Path) -> None:
    task_id = add_task(tmp_path, "Buy milk")

    task = next(
        item
        for item in load_tasks(tmp_path / "tasks.json")["tasks"]
        if item["id"] == task_id
    )
    assert task["priority"] == "medium"


def test_list_sorts_by_priority_then_id(tmp_path: Path) -> None:
    add_task(tmp_path, "Medium one", "--priority", "medium")
    add_task(tmp_path, "High one", "--priority", "high")
    add_task(tmp_path, "Low one", "--priority", "low")
    add_task(tmp_path, "High two", "--priority", "high")
    storage_path = tmp_path / "tasks.json"
    data = load_tasks(storage_path)
    data["tasks"].reverse()
    storage_path.write_text(json.dumps(data), encoding="utf-8")

    result = run_cli(tmp_path, "list", "--sort", "priority")

    assert result.returncode == 0, result.stderr
    rows = [line.split("\t") for line in result.stdout.splitlines()]
    assert [row[1] for row in rows] == ["High one", "High two", "Medium one", "Low one"]
    assert [int(row[0]) for row in rows[:2]] == sorted(int(row[0]) for row in rows[:2])


def test_list_filters_tags_case_insensitively(tmp_path: Path) -> None:
    add_task(tmp_path, "Work task", "--tag", "Work")
    add_task(tmp_path, "Home task", "--tag", "home")

    result = run_cli(tmp_path, "list", "--tag", "wOrK")

    assert result.returncode == 0, result.stderr
    assert len(result.stdout.splitlines()) == 1
    assert "Work task" in result.stdout
    assert "Home task" not in result.stdout


def test_list_no_matches_emits_no_task_lines(tmp_path: Path) -> None:
    add_task(tmp_path, "Work task", "--tag", "Work")

    result = run_cli(tmp_path, "list", "--tag", "missing")

    assert result.returncode == 0, result.stderr
    assert result.stdout == ""


def test_list_formats_all_fields_and_missing_values(tmp_path: Path) -> None:
    add_task(tmp_path, "Plain task")

    result = run_cli(tmp_path, "list")

    assert result.returncode == 0, result.stderr
    assert re.fullmatch(r"1\tPlain task\topen\t-\tmedium\n", result.stdout)


def test_complete_marks_task_done_without_output(tmp_path: Path) -> None:
    task_id = add_task(tmp_path, "Buy milk")

    result = run_cli(tmp_path, "complete", str(task_id))

    assert result.returncode == 0, result.stderr
    assert result.stdout == ""
    assert result.stderr == ""
    task = load_tasks(tmp_path / "tasks.json")["tasks"][0]
    assert task["status"] == "done"


def test_complete_done_task_is_noop(tmp_path: Path) -> None:
    task_id = add_task(tmp_path, "Buy milk")
    run_cli(tmp_path, "complete", str(task_id))
    before = (tmp_path / "tasks.json").read_bytes()

    result = run_cli(tmp_path, "complete", str(task_id))

    assert result.returncode == 0, result.stderr
    assert result.stdout == ""
    assert (tmp_path / "tasks.json").read_bytes() == before


def test_delete_removes_existing_task_without_output(tmp_path: Path) -> None:
    task_id = add_task(tmp_path, "Buy milk")

    result = run_cli(tmp_path, "delete", str(task_id))
    listing = run_cli(tmp_path, "list")

    assert result.returncode == 0, result.stderr
    assert result.stdout == ""
    assert result.stderr == ""
    assert listing.returncode == 0, listing.stderr
    assert listing.stdout == ""


def test_delete_unknown_id_reports_error(tmp_path: Path) -> None:
    result = run_cli(tmp_path, "delete", "999")

    assert result.returncode == 1
    assert result.stdout == ""
    assert result.stderr.strip()


def test_tasks_persist_across_invocations(tmp_path: Path) -> None:
    storage_path = tmp_path / "custom.json"
    task_id = add_task(tmp_path, "Persistent", "--tag", "Work", data_path=storage_path)

    result = run_cli(tmp_path, "list", data_path=storage_path)

    assert result.returncode == 0, result.stderr
    assert f"{task_id}\tPersistent\topen\tWork\tmedium" in result.stdout


def test_default_storage_path_when_environment_unset(tmp_path: Path) -> None:
    result = run_cli(tmp_path, "add", "Default path", unset_data_path=True)

    assert result.returncode == 0, result.stderr
    assert (tmp_path / "data" / "tasks.json").exists()
    assert len(load_tasks(tmp_path / "data" / "tasks.json")["tasks"]) == 1


@pytest.mark.parametrize("title", ["", " ", "\t\n", "x" * 201])
def test_add_rejects_empty_whitespace_and_overlong_titles(
    tmp_path: Path, title: str
) -> None:
    result = run_cli(tmp_path, "add", title)

    assert result.returncode == 1
    assert result.stdout == ""
    assert result.stderr.strip()
    assert not (tmp_path / "tasks.json").exists()


@pytest.mark.parametrize("title", ["x", "x" * 200])
def test_add_accepts_title_length_boundaries(tmp_path: Path, title: str) -> None:
    task_id = add_task(tmp_path, title)
    task = next(
        item
        for item in load_tasks(tmp_path / "tasks.json")["tasks"]
        if item["id"] == task_id
    )

    assert task["title"] == title


def test_title_length_counts_unicode_code_points(tmp_path: Path) -> None:
    title = "😀" * 200

    task_id = add_task(tmp_path, title)
    task = next(item for item in load_tasks(tmp_path / "tasks.json")["tasks"]
                if item["id"] == task_id)

    assert task["title"] == title


@pytest.mark.parametrize("priority", ["urgent", "HIGH", ""])
def test_invalid_priority_does_not_change_storage(
    tmp_path: Path, priority: str
) -> None:
    add_task(tmp_path, "Existing")
    before = (tmp_path / "tasks.json").read_bytes()

    result = run_cli(tmp_path, "add", "Rejected", "--priority", priority)

    assert result.returncode == 1
    assert result.stdout == ""
    assert result.stderr.strip()
    assert (tmp_path / "tasks.json").read_bytes() == before


@pytest.mark.parametrize("contents", ["{", "[]", '{"next_id": 1, "tasks": [{}]}'])
def test_invalid_storage_is_reported_without_modification(
    tmp_path: Path, contents: str
) -> None:
    storage_path = tmp_path / "tasks.json"
    storage_path.write_text(contents, encoding="utf-8")
    before = storage_path.read_bytes()

    result = run_cli(tmp_path, "list", data_path=storage_path)

    assert result.returncode == 1
    assert result.stdout == ""
    assert result.stderr.strip()
    assert storage_path.read_bytes() == before


def test_unreadable_storage_is_reported_without_replacement(tmp_path: Path) -> None:
    storage_path = tmp_path / "tasks.json"
    storage_path.mkdir()

    result = run_cli(tmp_path, "list", data_path=storage_path)

    assert result.returncode == 1
    assert result.stdout == ""
    assert result.stderr.strip()
    assert storage_path.is_dir()


def test_complete_unknown_id_reports_error(tmp_path: Path) -> None:
    result = run_cli(tmp_path, "complete", "999")

    assert result.returncode == 1
    assert result.stdout == ""
    assert result.stderr.strip()
