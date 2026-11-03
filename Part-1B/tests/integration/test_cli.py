import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_cli_surfaces_errors_on_stderr_with_nonzero_exit(tmp_path) -> None:
    result = subprocess.run(
        [sys.executable, "-m", "src.cli", "remind me to call mom tomorrow"],
        cwd=ROOT,
        env={"PYTHONPATH": str(ROOT), "MODEL_API_KEY": "", "MODEL_NAME": ""},
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert result.stdout == ""
    assert result.stderr.strip()


def test_cli_emits_one_json_line(monkeypatch, capsys) -> None:
    from src import cli

    expected = {
        "intent": "clarify",
        "title": None,
        "due_datetime": None,
        "clarification_question": "What do you mean?",
    }
    monkeypatch.setattr(cli, "parse_reminder", lambda sentence: expected)

    assert cli.main(["tomorrow"]) == 0
    captured = capsys.readouterr()

    assert captured.out == cli.serialize_response(expected)
    assert captured.out.count("\n") == 1
    assert captured.err == ""


def test_cli_serialization_is_compact_json() -> None:
    from src.cli import serialize_response

    payload = {
        "intent": "clarify",
        "title": None,
        "due_datetime": None,
        "clarification_question": "What do you mean?",
    }

    encoded = serialize_response(payload)

    assert encoded.endswith("\n")
    assert json.loads(encoded) == payload
    assert "\n" not in encoded.rstrip("\n")
