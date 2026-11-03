#!/usr/bin/env python3
"""Deterministic harness for Part 1A: lint, SAST and tests, recorded as JSON evidence."""
import datetime
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "harness-results"

GATES = {
    "lint": [sys.executable, "-m", "ruff", "check", "src", "tests"],
    "security": [sys.executable, "-m", "bandit", "-r", "src", "-q"],
    "tests": [sys.executable, "-m", "pytest", "tests", "-q"],
}


def run_gate(name, cmd):
    proc = subprocess.run(cmd, check=False, cwd=ROOT, capture_output=True, text=True)
    return {
        "gate": name,
        "command": " ".join(cmd),
        "exit_code": proc.returncode,
        "passed": proc.returncode == 0,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def main():
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    results = [run_gate(name, cmd) for name, cmd in GATES.items()]
    overall = all(r["passed"] for r in results)

    report = {"timestamp": stamp, "overall": "PASS" if overall else "FAIL", "gates": results}
    out = EVIDENCE / f"run-{stamp}.json"
    out.write_text(json.dumps(report, indent=2))

    for r in results:
        print(f"[{r['gate']}] {'PASS' if r['passed'] else 'FAIL'}")
    print(f"Overall: {report['overall']} -> {out.relative_to(ROOT)}")
    return 0 if overall else 1


if __name__ == "__main__":
    sys.exit(main())
