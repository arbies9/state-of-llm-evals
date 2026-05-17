# Scoring rubric

Each tool is scored 1–5 on the following axes. Total is **weighted**, not summed — see weights below.

## Axes

### 1. Developer ergonomics (weight: 0.20)
How fast can a competent engineer go from `npm install` (or `pip install`) to a passing eval in CI? Includes docs quality, sane defaults, helpful errors.

- **5** — Working eval in <30 min, no surprises
- **3** — Working eval in a half-day, some docs spelunking
- **1** — Needs a champion who's already used it

### 2. CI integration (weight: 0.15)
Can it run as a check on every PR? Does it produce a diffable output the team can review?

- **5** — First-class GitHub Action, structured output, PR comment
- **3** — Runs in CI but you wire the reporting yourself
- **1** — Requires hosted-only access; CI is an afterthought

### 3. Cost transparency (weight: 0.15)
Can you see what each eval run cost, attributed by model/route/dataset? Critical for TPMs justifying eval budget.

- **5** — Built-in cost view, exportable, multi-currency
- **3** — Token counts only; you do the math
- **1** — Opaque

### 4. Multi-model support (weight: 0.15)
Can you run the same eval against OpenAI, Anthropic, OSS via Ollama/vLLM, etc., without rewriting?

- **5** — First-class provider abstraction
- **3** — Works via a generic HTTP adapter you maintain
- **1** — Effectively single-provider

### 5. Output analysis (weight: 0.15)
Does it help you understand *why* eval scores changed between runs? Regressions, slice analysis, failure clustering.

- **5** — Run-over-run diff UI + failure clustering
- **3** — Per-prompt drill-down, no slicing
- **1** — Pass/fail only

### 6. OSS posture (weight: 0.10)
License, self-host story, whether the OSS version is the real product or a stripped-down trial.

- **5** — Permissive license, hosted is convenience-only
- **3** — Open core with meaningful gaps
- **1** — Source-available or hosted-only

### 7. Safety/red-team primitives (weight: 0.10)
Does it have first-class support for adversarial prompts, jailbreak suites, PII leak checks?

- **5** — Built-in red-team modes, maintained adversarial datasets
- **3** — Possible but DIY
- **1** — Not in scope

## Why these weights

This rubric is tuned for **mid-size product teams** shipping LLM features — not research labs, not solo hackers. If your context is different, fork this file and re-weight.

- Dev ergonomics gets the highest weight because every other axis is irrelevant if the team won't actually use the tool.
- CI / cost / multi-model / output analysis are tied at 0.15 — they're the operational backbone.
- OSS posture and safety primitives are lower not because they don't matter, but because most teams adopt their first eval tool before they have a mature view on either.

## What's explicitly excluded

- Hosted UI beauty (subjective, changes monthly).
- Per-seat pricing (it's documented per tool but not scored — too org-specific).
- Brand / funding signal.
- Integrations with niche frameworks not used by the sample workload.
