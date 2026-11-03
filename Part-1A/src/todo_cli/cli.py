from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from todo_cli.storage import JsonTaskStorage, StorageError, TaskStore
from todo_cli.task import InvalidStatusTransition, Task, TaskNotFoundError
from todo_cli.validation import ValidationError, validate_priority, validate_title

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="todo")
    commands = parser.add_subparsers(dest="command", required=True)

    add_parser = commands.add_parser("add")
    add_parser.add_argument("title")
    add_parser.add_argument("--tag")
    add_parser.add_argument("--priority")

    list_parser = commands.add_parser("list")
    list_parser.add_argument("--tag")
    list_parser.add_argument("--sort", choices=("priority",))

    complete_parser = commands.add_parser("complete")
    complete_parser.add_argument("id", type=int)

    delete_parser = commands.add_parser("delete")
    delete_parser.add_argument("id", type=int)
    return parser


def _escape_field(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace("\t", "\\t")
        .replace("\n", "\\n")
        .replace("\r", "\\r")
    )


def _format_task(task: Task) -> str:
    tag = task.tag if task.tag is not None else "-"
    priority = task.priority if task.priority is not None else "-"
    fields = (str(task.id), task.title, task.status, tag, priority)
    return "\t".join(_escape_field(field) for field in fields)


def _list_tasks(store: TaskStore, tag_filter: str | None, sort_by: str | None) -> None:
    tasks = store.tasks
    if tag_filter is not None:
        normalized_filter = tag_filter.casefold()
        tasks = [
            task
            for task in tasks
            if task.tag is not None and task.tag.casefold() == normalized_filter
        ]

    if sort_by == "priority":
        tasks = sorted(
            tasks,
            key=lambda task: (PRIORITY_ORDER.get(task.priority, 3), task.id),
        )
    else:
        tasks = sorted(tasks, key=lambda task: task.id)

    for task in tasks:
        print(_format_task(task))


def _run(args: argparse.Namespace) -> int:
    storage = JsonTaskStorage()
    if args.command == "add":
        title = validate_title(args.title)
        priority = validate_priority(args.priority)
        store = storage.load()
        task = Task(
            id=store.next_id,
            title=title,
            tag=args.tag,
            priority=priority,
        )
        store.tasks.append(task)
        store.next_id += 1
        storage.save(store)
        print(task.id)
        return 0

    store = storage.load()
    if args.command == "list":
        _list_tasks(store, args.tag, args.sort)
        return 0

    task = next((item for item in store.tasks if item.id == args.id), None)
    if task is None:
        raise TaskNotFoundError(f"Task with ID {args.id} does not exist")

    if args.command == "complete":
        was_done = task.status == "done"
        task.transition_to("done")
        if not was_done:
            storage.save(store)
        return 0

    store.tasks.remove(task)
    storage.save(store)
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return _run(args)
    except (
        InvalidStatusTransition,
        StorageError,
        TaskNotFoundError,
        ValidationError,
    ) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
