"""Shared loader for the canonical resume-bullet dataset.

Returns plain dicts so the standalone mock script doesn't need to import
inspect_ai. The real Inspect entry point converts these to `Sample`
objects locally.

Row shape:
    {"input": str, "metadata": {"id", "domain", "expected_themes"}}

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
        # The mock modes rely on JS/Python hash parity, which only holds for
        # trimmed ASCII inputs (JS hashes UTF-16 code units, Python code points).
        assert row["input"].isascii() and row["input"] == row["input"].strip(), (
            f"row {row['id']}: input must be trimmed ASCII for JS/Python hash parity"
        )
        rows.append(
            {
                "input": row["input"],
                "metadata": {
                    "id": row["id"],
                    "domain": row["domain"],
                    "expected_themes": row["expected_themes"],
                },
            }
        )
    return rows
