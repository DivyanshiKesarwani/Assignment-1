import json

from todo_cli.storage import JsonTaskStorage, TaskStore


def test_missing_file_loads_empty_store(tmp_path) -> None:
    storage = JsonTaskStorage(tmp_path / "tasks.json")

    assert storage.load() == TaskStore(tasks=[], next_id=1)


def test_save_and_load_round_trip(tmp_path) -> None:
    storage = JsonTaskStorage(tmp_path / "tasks.json")
    data = {
        "next_id": 2,
        "tasks": [
            {
                "id": 1,
                "title": "Buy milk",
                "status": "open",
                "tag": None,
                "priority": "medium",
            }
        ],
    }

    storage.path.write_text(json.dumps(data), encoding="utf-8")

    loaded = storage.load()

    assert loaded.next_id == 2
    assert [task.to_dict() for task in loaded.tasks] == data["tasks"]
