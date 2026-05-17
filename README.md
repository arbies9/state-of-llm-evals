# State of LLM Evals (2026)

> An opinionated, methodology-first comparison of the tools people actually use to evaluate LLM applications: **Promptfoo, Braintrust, LangSmith, Inspect, and Ragas**.

This is a working deep-dive, not a marketing matrix. The point is to help a tech lead or TPM pick the right eval stack for a given team — and to show their reasoning in writing.

---

## TL;DR (preview — full ratings in [`comparison.md`](./comparison.md))

| Tool | Best for | Watch out for |
|---|---|---|
| **Promptfoo** | OSS-first teams, CI-friendly red-teaming | Limited hosted UI; you build the analysis layer |
| **Braintrust** | Teams that want a polished hosted product, fast | Vendor lock-in; pricing scales with traces |
| **LangSmith** | Teams already on LangChain / LangGraph | Tightly coupled to the LC stack |
| **Inspect** (UK AISI) | Safety / capability research, rigorous evals | Steeper ramp; less app-developer ergonomics |
| **Ragas** | RAG-specific eval (faithfulness, context recall) | Narrow scope — not a general eval framework |

Full ratings are computed from the rubric in [`methodology/rubric.md`](./methodology/rubric.md), not vibes.

---

## What you'll find here

- **[`methodology/`](./methodology/)** — how each tool was scored: rubric, weights, the sample app used as a workload, and what's deliberately excluded.
- **[`tools/`](./tools/)** — one markdown brief per tool: setup cost, primitives, where it shines, where it bites.
- **[`benchmark/`](./benchmark/)** — a tiny sample eval (resume-bullet rewriter) implemented in each framework, so the comparison is grounded in actual code.
- **[`comparison.md`](./comparison.md)** — the synthesized matrix and the recommendation flow.

---

## Why I'm writing this

Eval tooling is the most under-discussed and most decision-shaping part of an LLM app. The wrong choice burns months of engineering trust. There are good per-tool docs and a lot of vendor blog posts, but very little **side-by-side, methodology-first** writing.

This is also a deliberate TPM artifact for my portfolio: a real RFC-style comparison with a recommendation, not a feature checklist.

---

## Methodology in one sentence

Run the same eval workload through every tool, score each on a fixed rubric (developer ergonomics, CI integration, cost transparency, multi-model support, output analysis, OSS posture), weight by what mid-size product teams actually care about, and write down where the scores disagreed with my gut.

Full version: [`methodology/rubric.md`](./methodology/rubric.md).

---

## Status

- [x] Tool list locked
- [x] Rubric drafted
- [x] Sample workload implemented (resume-bullet rewriter, 50 prompts)
- [ ] Per-tool implementations (1 of 5 — Promptfoo done; Braintrust, LangSmith, Inspect, Ragas pending)
- [ ] Scoring pass
- [ ] First public draft
- [ ] Open for review / corrections

I'd rather be slow and right than fast and wrong on this one. PRs and corrections welcome — especially from people who actually ship one of these.
