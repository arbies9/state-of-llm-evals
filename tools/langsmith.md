# LangSmith

> **Status:** draft brief based on building the implementation in [`benchmark/langsmith/`](../benchmark/langsmith/). Rubric scores are provisional until a full scoring pass against a real LangSmith account. See [README status](../README.md#status).

## 1. Pitch

LangChain's eval + observability product. Hosted dashboard with tracing, datasets, experiments, and a prompt playground. SDK is Python and TypeScript. The eval primitive is `langsmith.evaluate(task, data=, evaluators=)`. Tracing piggybacks on LangChain runs but works fine for plain Python/TS functions too. Free tier covers small projects; pricing scales with traces and seats — same model as Braintrust.

## 2. Setup cost

About 30 minutes from zero:

1. Create a free account at smith.langchain.com, grab `LANGSMITH_API_KEY` (~5 min)
2. `pip install langsmith openai` (1 min)
3. Write the `task(inputs)` callable, a few `evaluator(run, example)` functions, and the `evaluate(...)` call (~20 min for our workload — the docs are clear on the function signatures)
4. `python3 eval_resume_bullets.py` (1 min)

[`benchmark/langsmith/`](../benchmark/langsmith/) is ~390 lines of Python across four files — ~240 excluding the offline mock runner. The friction point: the SDK has had multiple eval API generations (`evaluate` vs `aevaluate` vs decorator-based), and finding the canonical current pattern took some doc spelunking. Worth knowing about before you start.

## 3. Primitives

- **Project** — workspace-level container; created automatically.
- **Dataset** — a named collection of `Example`s living server-side. Can be created from the UI, the SDK, or inline at eval-time.
- **Example** — one row of `{inputs, outputs, metadata}`.
- **Run** — one task invocation; carries `outputs`, tracing spans, tokens, cost.
- **Experiment** — one call to `evaluate()`; appears in the UI as a named row of results.
- **Evaluator** — a callable `(run, example) -> {"key", "score", "comment"}`.
- **Tracing** — auto-instrumented LLM call spans when `LANGSMITH_TRACING=true`; integrates deeply with LangChain but works for plain functions too.

## 4. Where it shines

- **Best-in-class tracing.** Every call inside `task` (and inside LangChain agents, if you're using them) shows up as a nested span in the run view. For agent/chain-style evals, this is what justifies adopting LangSmith over either alternative above.
- **Datasets live on the platform.** Once you upload a dataset, every experiment is comparable against every other on the same data — diff views are clean.
- **Native LangChain integration.** If you're already using LangChain or LangGraph, evals work with zero wiring; you get traces, prompt versions, and run history for free.
- **The free tier is generous for early teams.** A small team running daily evals fits comfortably.

## 5. Where it bites

- **Coupled to the LangChain ecosystem in a way that shows up in the docs.** LangSmith is technically framework-agnostic, but tutorials and reference patterns assume LangChain. Teams not using LangChain end up reading between the lines.
- **API surface has churn.** Multiple eval-call generations (`evaluate`, `aevaluate`, `@evaluator`, dataset-as-string vs inline) make searching for examples a coin-flip on whether the answer is current.
- **No first-class red-team primitives.** Same as Braintrust — possible to build, nothing prebuilt.
- **Hosted-first.** OSS components exist (langsmith SDK is OSS, smith.langchain.com is not). Self-host is not a story.
- **Pricing scales with traces.** Same shape as Braintrust; budget accordingly if you run nightly evals in CI.

## 6. My rubric scores (DRAFT)

> Scoring methodology: [`methodology/rubric.md`](../methodology/rubric.md). Numbers below are provisional from building the implementation; will be re-confirmed during the scoring pass once an actual LangSmith account has been used end-to-end.

| Axis | Weight | Score | Reasoning |
|---|---|---|---|
| Developer ergonomics | 0.20 | **3** | Once you find the right `evaluate()` API generation it's clean — but the API churn and LangChain-flavored docs cost half a star. |
| CI integration | 0.15 | **4** | `python3 eval_*.py` works in CI; exit codes + LangSmith run links are clean. PR comments are a separate wire-up. |
| Cost transparency | 0.15 | **4** | Tokens and dollar cost surface per run + per experiment in the UI. Slight edge to Braintrust on aggregate/project rollups. |
| Multi-model support | 0.15 | **4** | Via LangChain providers or direct SDK calls. Slight edge to Promptfoo for first-class provider abstractions outside the LangChain ecosystem. |
| Output analysis | 0.15 | **5** | Run/experiment diff views are excellent; tracing makes failure analysis trivial for any task with intermediate steps. |
| OSS posture | 0.10 | **2** | SDK is OSS, the product is not. Same posture as Braintrust. |
| Safety / red-team | 0.10 | **2** | Possible to build via custom evaluators + datasets; no prebuilt red-team mode. |

**Weighted total (draft): 3.55 / 5.**

## 7. Open questions before final scoring

- Validate the cost-transparency score with a real experiment — is the project-level cost rollup as good as Braintrust's?
- Re-time the "setup cost" against a teammate going through it cold to confirm the 30-min estimate isn't optimistic.
- Try the eval with a LangChain-based task (just for fairness) to see whether the dev-ergo score goes up when the tool's preferred shape matches the user's shape.
