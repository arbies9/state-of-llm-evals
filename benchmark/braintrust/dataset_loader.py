"""Shared loader for the canonical resume-bullet dataset.

Every tool implementation reads from ../dataset.jsonl so the workload stays
identical across frameworks. This module returns rows in Braintrust's
expected Eval data shape:

    {"input": str, "expected": None, "metadata": {"id", "domain", "expected_themes"}}
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterator

DATASET_PATH = Path(__file__).resolve().parent.parent / "dataset.jsonl"


def load_dataset() -> list[dict]:
    rows = []
    for line in DATASET_PATH.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        rows.append(
            {
                "input": row["input"],
                "expected": None,
                "metadata": {
                    "id": row["id"],
                    "domain": row["domain"],
                    "expected_themes": row["expected_themes"],
                },
            }
        )
    return rows


def iter_dataset() -> Iterator[dict]:
    yield from load_dataset()
