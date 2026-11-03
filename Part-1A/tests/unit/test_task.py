import pytest

from todo_cli.task import InvalidStatusTransition, Task


def test_transition_open_to_done() -> None:
    task = Task(id=1, title="Buy milk")

    task.transition_to("done")

    assert task.status == "done"


@pytest.mark.parametrize("target", ["open", "pending", "archived"])
def test_rejects_transitions_other_than_open_to_done(target: str) -> None:
    task = Task(id=1, title="Buy milk")
    task.transition_to("done")

    with pytest.raises(InvalidStatusTransition):
        task.transition_to(target)


def test_completing_done_task_is_idempotent() -> None:
    task = Task(id=1, title="Buy milk")
    task.transition_to("done")

    task.transition_to("done")

    assert task.status == "done"
