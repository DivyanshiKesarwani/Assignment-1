from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

from todo_cli.task import Task
from todo_cli.validation import ValidationError, validate_store_data


class StorageError(ValueError):
    """Raised when task storage cannot be read or written safely."""


@dataclass
class TaskStore:
    tasks: list[Task]
    next_id: int

    def to_dict(self) -> dict:
        return {
            "next_id": self.next_id,
            "tasks": [task.to_dict() for task in self.tasks],
        }


class JsonTaskStorage:
    def __init__(self, path: Path | None = None) -> None:
        if path is None:
            path = Path(os.environ.get("TODO_DATA_PATH", "./data/tasks.json"))
        self.path = Path(path)

    def load(self) -> TaskStore:
        try:
            with self.path.open("r", encoding="utf-8") as task_file:
                data = json.load(task_file)
        except FileNotFoundError:
            return TaskStore(tasks=[], next_id=1)
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            raise StorageError(f"Cannot read task data: {error}") from error

        try:
            tasks, next_id = validate_store_data(data)
        except ValidationError as error:
            raise StorageError(f"Invalid task data: {error}") from error
        return TaskStore(tasks=tasks, next_id=next_id)

    def save(self, store: TaskStore) -> None:
        data = store.to_dict()
        try:
            validate_store_data(data)
        except ValidationError as error:
            raise StorageError(
                f"Refusing to save invalid task data: {error}"
            ) from error

        temporary_path = None
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=str(self.path.parent),
                prefix=f".{self.path.name}.",
                suffix=".tmp",
                delete=False,
            ) as task_file:
                temporary_path = Path(task_file.name)
                json.dump(data, task_file, ensure_ascii=False, indent=2)
                task_file.write("\n")
            os.replace(str(temporary_path), str(self.path))
        except (OSError, TypeError, ValueError) as error:
            if temporary_path is not None:
                try:
                    temporary_path.unlink()
                except FileNotFoundError:
                    pass
            raise StorageError(f"Cannot write task data: {error}") from error
