#!/usr/bin/env bash
# State of LLM Evals — run all four tool mocks end-to-end.
# No API keys, no accounts, no cost. The first run downloads the pinned
# promptfoo CLI from npm; everything after that is offline. This is the
# single project-level command for the repo.

cd "$(dirname "$0")"

# Pinned: the table parser below depends on this version's results JSON
# shape, and the Promptfoo mock judge's verdicts depend on this version's
# llm-rubric grading template.
PROMPTFOO_VERSION="0.121.15"

# Keep local smoke tests from leaving __pycache__ folders behind.
export PYTHONDONTWRITEBYTECODE=1

bar() { printf '═%.0s' $(seq 1 72); echo; }

bar
echo "  State of LLM Evals — running all four tool mocks (no API keys, no cost)"
bar

FAILED_TOOLS=""

run_mock() {
  local name=$1
  local dir=$2
  local cmd=$3
  local lines=${4:-200}
  echo
  echo "▶ ${name}"
  echo "  ────────────────────────────────────────────────────────"
  # Never let a stale results file from an earlier run mask a failure.
  rm -f "$dir/results.mock.json"
  ( cd "$dir" && bash -c "$cmd" ) 2>&1 | tail -n "$lines" | sed 's/^/  /'
  local status=${PIPESTATUS[0]}
  local why=""
  [ -f "$dir/results.mock.json" ] || why=", no results.mock.json written"
  if [ "$status" -ne 0 ] || [ -n "$why" ]; then
    echo "  ✖ ${name} FAILED (exit ${status}${why})"
    FAILED_TOOLS="${FAILED_TOOLS}${FAILED_TOOLS:+, }${name}"
  fi
}

# PROMPTFOO_FAILED_TEST_EXIT_CODE=0: the mock guarantees some assertion
# failures by design, so a non-zero exit should mean a real error, not a
# failing eval row.
run_mock "Promptfoo (JS)"   "benchmark/promptfoo"   "PROMPTFOO_FAILED_TEST_EXIT_CODE=0 npx --yes promptfoo@${PROMPTFOO_VERSION} eval -c promptfooconfig.mock.yaml" 10
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

def pf():
    path = Path("benchmark/promptfoo/results.mock.json")
    if not path.exists():
        return None
    data = json.loads(path.read_text())
    rows = data.get("results", {}).get("results") or data.get("results", [])
    tally = {}
    for row in rows:
        for a in ((row.get("gradingResult") or {}).get("componentResults") or []):
            m = (a.get("assertion") or {}).get("metric") or "?"
            tally.setdefault(m, {"pass": 0, "fail": 0})
            tally[m]["pass" if a.get("pass") else "fail"] += 1
    return tally

def py(tool):
    path = Path(f"benchmark/{tool}/results.mock.json")
    if not path.exists():
        return None
    return json.loads(path.read_text())["tallies"]

tools = [("Promptfoo", pf()), ("Braintrust", py("braintrust")),
         ("LangSmith", py("langsmith")), ("Inspect", py("inspect"))]

def fmt(tallies, metric):
    if tallies is None or metric not in tallies:
        return "—"
    t = tallies[metric]
    n = t["pass"] + t["fail"]
    return f"{t['pass']}/{n} ({t['pass']/n*100:.0f}%)"

print()
print(f"  {'Metric':<16}" + "".join(f"{name:<14}" for name, _ in tools))
print("  " + "─" * (16 + 14 * len(tools)))
for m in ["faithfulness", "theme_coverage", "style", "length"]:
    print(f"  {m:<16}" + "".join(f"{fmt(t, m):<14}" for _, t in tools))
print()
missing = [name for name, t in tools if t is None]
if missing:
    print(f"  '—' = no results for {', '.join(missing)} (that mock failed above).")
print("  Programmatic metrics (theme_coverage, length) match across all four")
print("  tools by design. The three Python mocks share a judge seed, so their")
print("  judge numbers match each other; Promptfoo's mock judge seeds on its")
print("  rendered grading prompt and differs slightly.")
print()
PY

if [ -n "$FAILED_TOOLS" ]; then
  echo "  ✖ Failed: ${FAILED_TOOLS}"
  exit 1
fi
