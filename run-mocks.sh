#!/usr/bin/env bash
# State of LLM Evals — run all four tool mocks end-to-end.
# No API keys, no accounts, no cost. This is the single project-level
# command for the repo.

cd "$(dirname "$0")"

bar() { printf '═%.0s' $(seq 1 72); echo; }

bar
echo "  State of LLM Evals — running all four tool mocks (offline)"
bar

run_mock() {
  local name=$1
  local dir=$2
  local cmd=$3
  echo
  echo "▶ ${name}"
  echo "  ────────────────────────────────────────────────────────"
  ( cd "$dir" && bash -c "$cmd" ) 2>&1 | sed 's/^/  /'
}

run_mock "Promptfoo (JS)"   "benchmark/promptfoo"   "npx --yes promptfoo@latest eval -c promptfooconfig.mock.yaml | tail -10"
run_mock "Braintrust (PY)"  "benchmark/braintrust"  "python3 eval_mock.py"
run_mock "LangSmith (PY)"   "benchmark/langsmith"   "python3 eval_mock.py"
run_mock "Inspect (PY)"     "benchmark/inspect"     "python3 eval_mock.py"

echo
bar
echo "  Side-by-side per-metric pass rates"
bar

python3 - <<'PY'
import json
from pathlib import Path

BENCH = Path(__file__).resolve().parent / "benchmark" if "__file__" in dir() else Path("benchmark")

def pf():
    data = json.loads((Path("benchmark/promptfoo/results.mock.json")).read_text())
    rows = data.get("results", {}).get("results") or data.get("results", [])
    tally = {}
    for row in rows:
        for a in ((row.get("gradingResult") or {}).get("componentResults") or []):
            m = (a.get("assertion") or {}).get("metric") or "?"
            tally.setdefault(m, {"pass": 0, "fail": 0})
            tally[m]["pass" if a.get("pass") else "fail"] += 1
    return tally

def py(tool):
    return json.loads(Path(f"benchmark/{tool}/results.mock.json").read_text())["tallies"]

tools = [("Promptfoo", pf()), ("Braintrust", py("braintrust")),
         ("LangSmith", py("langsmith")), ("Inspect", py("inspect"))]

def fmt(t):
    n = t["pass"] + t["fail"]
    return f"{t['pass']}/{n} ({t['pass']/n*100:.0f}%)"

print()
print(f"  {'Metric':<16}" + "".join(f"{name:<14}" for name, _ in tools))
print("  " + "─" * (16 + 14 * len(tools)))
for m in ["faithfulness", "theme_coverage", "style", "length"]:
    print(f"  {m:<16}" + "".join(f"{fmt(t[m]):<14}" for _, t in tools))
print()
print("  Programmatic metrics (theme_coverage, length) match across all four")
print("  tools by design. Judge metrics use independent mock noise.")
print()
PY
