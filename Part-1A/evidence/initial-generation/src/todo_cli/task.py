from __future__ import annotations

from dataclasses import dataclass


class InvalidStatusTransition(ValueError):
    """Raised when a task is assigned a disallowed status."""


class TaskNotFoundError(ValueError):
    """Raised when an operation references an unknown task ID."""


@dataclass
class Task:
    id: int
    title: str
    status: str = "open"
    tag: str | None = None
    priority: str | None = "medium"

    def transition_to(self, target: str) -> None:
        if self.status == "done" and target == "done":
            return
        if self.status != "open" or target != "done":
            raise InvalidStatusTransition(
                f"Task status cannot transition from {self.status!r} to {target!r}"
            )
        self.status = "done"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status,
            "tag": self.tag,
            "priority": self.priority,
        }
