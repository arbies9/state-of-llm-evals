# State of LLM Evals

> An opinionated, methodology-first comparison of the tools people actually use to evaluate LLM applications: **Promptfoo, Braintrust, LangSmith, Inspect, and Ragas**.

This is a working deep-dive, not a marketing matrix. It's the artifact a TPM or eng lead can cite when explaining *"why we picked X"* to leadership, engineers, and finance — grounded in working implementations across all five frameworks, not vendor positioning.

## Run it locally (no API keys, no cost)

Two single-command entry points, depending on what you want:

```bash
./run-docs.sh        # browse the docs at http://localhost:3000 (needs: node)
./run-mocks.sh       # run all four tool mocks + side-by-side table (needs: node, python3)
```

- **`./run-docs.sh`** spins up a local markdown server so you can read the README, methodology, tool briefs, and benchmark docs as rendered pages — the same experience as the GitHub repo but offline. Ctrl+C to stop.
- **`./run-mocks.sh`** runs the same 50-bullet eval workload through all four implemented tools in mock mode (~10 seconds), then prints per-metric pass-rate columns side by side. The "does this project actually work" check.

Neither needs an account, an API key, or any spend.

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

## Who this is for

A **TPM, eng lead, or staff engineer** making a defensible eval-tool choice for an LLM-shipping product team — and who has to explain that choice to leadership, finance, and the engineers who'll actually use it.

The rubric is tuned for **mid-size product teams (5-30 engineers) shipping LLM features in product**, not solo hackers or research labs. If your context is different — regulated industry where safety should weigh 0.30 instead of 0.10, a research lab grading capability benchmarks, an early-stage team where cost dominates — the rubric is forkable. Re-weight first, then read.

What this artifact gets you that vendor blog posts and Twitter threads don't:

- A **defensible** recommendation, not a vibes-based one. You can point to the rubric, the weights, the per-tool scores, and the working implementation that backs the brief.
- A **shared vocabulary** between TPM and engineers. The same per-tool brief is useful to both — "Where it bites" is what the TPM needs for the decision doc; the implementation in `benchmark/<tool>/` is what the engineers want to read before committing.
- **Cost intuition** before contracts. Per-tool briefs name the pricing model (per-seat, per-trace, per-eval) so you walk into procurement with a realistic budget ask, not a vendor's "starting at $X/month" headline.
- A **template you can reuse.** When the same team needs to pick an observability tool, a feature-flag service, or any other infra decision, the methodology transfers. The rubric is forkable on purpose.

---

## What you'll find here

- **[`methodology/`](./methodology/)** — how each tool was scored: rubric, weights, the sample app used as a workload, and what's deliberately excluded.
- **[`tools/`](./tools/)** — one markdown brief per tool: setup cost, primitives, where it shines, where it bites, weighted rubric score.
- **[`benchmark/`](./benchmark/)** — the same 50-bullet eval workload (resume-bullet rewriter) implemented in each framework, so the briefs aren't vibes — there's working code behind every claim. Each subdir has a free `mock` mode that runs without API keys or accounts.
- **[`comparison.md`](./comparison.md)** — the synthesized matrix and the recommendation flow.

---

## How a TPM uses this

A concrete workflow for someone walking into the "which eval tool should we adopt?" decision:

1. **Skim TL;DR + rubric.** ~5 minutes. Decide whether the rubric weights match your team's context, or fork the rubric.
2. **Read the 2-3 briefs that match your situation.** Not all five — that's wasted time. The *"Where it bites"* section is the one to read carefully; those are the tradeoffs you'll have to defend to leadership and to your engineers.
3. **Send an engineer to `benchmark/<tool>/`.** ~20 minutes per tool. They sanity-check the brief's *"developer ergonomics"* claim against their own ramp — and they trust your recommendation more because you sent them to working code, not a vendor demo.
4. **Write your own RFC.** Cite this project as the analysis. Attach the weighted score. Own the decision.
5. *(Optional)* **Re-run the workload locally before procurement.** Each tool ships a `eval_mock.py` / mock config that runs offline in seconds. Useful for a 10-minute "does this look right" check before signing anything.

The thing this artifact saves you from: spending two weeks reading vendor blog posts and ending up with *"Promptfoo seems good?"* — a recommendation you can't defend when your CTO asks *"okay, but why not Braintrust."*

---

## Why this exists

The wrong eval-tool choice burns months of engineering trust, blows budget on traces nobody reviews, and locks you into vendor pricing that changes the moment your team becomes load-bearing on the tool. There are good per-tool docs and a lot of vendor blog posts; there is very little **side-by-side, methodology-first** writing a TPM can actually cite in a decision doc.

This is also a deliberate TPM portfolio artifact: a real RFC-style comparison with a recommendation, not a feature checklist.

---

## Methodology in one sentence

Run the same eval workload through every tool, score each on a fixed rubric (developer ergonomics, CI integration, cost transparency, multi-model support, output analysis, OSS posture), weight by what mid-size product teams actually care about, and write down where the scores disagreed with my gut.

Full version: [`methodology/rubric.md`](./methodology/rubric.md).

---

## Status

- [x] Tool list locked
- [x] Rubric drafted
- [x] Sample workload implemented (resume-bullet rewriter, 50 prompts)
- [x] Per-tool implementations (4 of 5 wired; Ragas is brief-only by design — see [`tools/ragas.md`](./tools/ragas.md) for why)
- [ ] Scoring pass
- [ ] First public draft
- [ ] Open for review / corrections

I'd rather be slow and right than fast and wrong on this one. PRs and corrections welcome — especially from people who actually ship one of these.
