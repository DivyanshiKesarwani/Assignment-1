from __future__ import annotations

from typing import Any

from todo_cli.task import Task


class ValidationError(ValueError):
    """Raised when task input or persisted task data is invalid."""


VALID_PRIORITIES = {"low", "medium", "high"}
VALID_STATUSES = {"open", "done"}
TASK_FIELDS = {"id", "title", "status", "tag", "priority"}


def validate_title(title: str) -> str:
    if not isinstance(title, str):
        raise ValidationError("Title must be text")
    if not title or title.isspace():
        raise ValidationError("Title must not be empty or whitespace-only")
    if len(title) > 200:
        raise ValidationError("Title must be at most 200 Unicode code points")
    return title


def validate_priority(priority: Any) -> str:
    if priority is None:
        return "medium"
    if not isinstance(priority, str) or priority not in VALID_PRIORITIES:
        raise ValidationError("Priority must be one of: low, medium, high")
    return priority


def validate_store_data(data: Any) -> tuple[list[Task], int]:
    if not isinstance(data, dict) or set(data) != {"next_id", "tasks"}:
        raise ValidationError("Task storage must contain next_id and tasks")

    next_id = data["next_id"]
    records = data["tasks"]
    if isinstance(next_id, bool) or not isinstance(next_id, int) or next_id < 1:
        raise ValidationError("next_id must be a positive integer")
    if not isinstance(records, list):
        raise ValidationError("tasks must be a list")

    tasks = []
    seen_ids = set()
    for record in records:
        task = validate_task_record(record)
        if task.id in seen_ids:
            raise ValidationError(f"Duplicate task ID: {task.id}")
        seen_ids.add(task.id)
        tasks.append(task)

    if seen_ids and next_id <= max(seen_ids):
        raise ValidationError("next_id must be greater than every task ID")
    return tasks, next_id


def validate_task_record(record: Any) -> Task:
    if not isinstance(record, dict) or set(record) != TASK_FIELDS:
        raise ValidationError(
            "Each task must contain id, title, status, tag, and priority"
        )

    task_id = record["id"]
    if isinstance(task_id, bool) or not isinstance(task_id, int) or task_id < 1:
        raise ValidationError("Task ID must be a positive integer")

    title = validate_title(record["title"])
    status = record["status"]
    if not isinstance(status, str) or status not in VALID_STATUSES:
        raise ValidationError("Task status must be open or done")

    tag = record["tag"]
    if tag is not None and not isinstance(tag, str):
        raise ValidationError("Task tag must be text or null")

    priority = record["priority"]
    if priority is not None:
        validate_priority(priority)

    return Task(
        id=task_id,
        title=title,
        status=status,
        tag=tag,
        priority=priority,
    )
