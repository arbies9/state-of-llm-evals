"""Shared loader for the canonical resume-bullet dataset.

Returns plain-dict rows:

    {"inputs": {"input": str}, "outputs": None, "metadata": {"id", "domain", "expected_themes"}}

These are consumed by eval_mock.py directly and by eval_resume_bullets.py's
one-time dataset upload (LangSmith's evaluate() wants a server-side dataset,
not raw dicts). Every tool implementation reads from ../dataset.jsonl so the
workload stays identical across frameworks.
"""

from __future__ import annotations

import json
from pathlib import Path

DATASET_PATH = Path(__file__).resolve().parent.parent / "dataset.jsonl"


def load_dataset() -> list[dict]:
    rows = []
    for line in DATASET_PATH.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        # The mock modes rely on JS/Python hash parity, which only holds for
        # trimmed ASCII inputs (JS hashes UTF-16 code units, Python code points).
        assert row["input"].isascii() and row["input"] == row["input"].strip(), (
            f"row {row['id']}: input must be trimmed ASCII for JS/Python hash parity"
        )
        rows.append(
            {
                "inputs": {"input": row["input"]},
                "outputs": None,
                "metadata": {
                    "id": row["id"],
                    "domain": row["domain"],
                    "expected_themes": row["expected_themes"],
                },
            }
        )
    return rows
