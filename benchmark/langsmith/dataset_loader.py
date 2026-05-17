"""Shared loader for the canonical resume-bullet dataset.

Returns rows in LangSmith's Example shape:

    {"inputs": {"input": str}, "outputs": None, "metadata": {"id", "domain", "expected_themes"}}

Every tool implementation reads from ../dataset.jsonl so the workload stays
identical across frameworks.
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
