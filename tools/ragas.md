# Ragas

> **Status:** brief-only by design. No `benchmark/ragas/` directory exists because the resume-bullet rewriter is not a RAG-shaped task and a Ragas implementation against it would be contrived. Scores below are provisional and grounded in Ragas's public docs, paper, and example code — *not* in hands-on implementation against our workload. See [Where it doesn't fit our workload](#7-where-it-doesnt-fit-our-workload) and [README status](../README.md#status).

## 1. Pitch

[Ragas](https://github.com/explodinggradients/ragas) is a Python library for evaluating **Retrieval-Augmented Generation** systems specifically. It is *not* a general eval framework — it's an opinionated metric library that expects a particular input shape (`question → retrieved_contexts → answer → optional ground_truth`) and computes a fixed set of metrics on top.

The value proposition is the metric set. Faithfulness, answer relevancy, context precision, and context recall together form the "RAG quadrant" — and you genuinely cannot get these from Promptfoo or Braintrust without writing them yourself, well.

## 2. Setup cost

Light if you already have a RAG pipeline; heavier if you don't:

```bash
pip install ragas openai
```

Then point Ragas at a dataset shaped as `Dataset` rows with `question`, `contexts`, `answer`, `ground_truth`. The metric calls are one-liners:

```python
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall

result = evaluate(
    dataset=hf_dataset,
    metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
)
```

Estimated 1-2 hours from `pip install` to first scores assuming you already have a RAG pipeline whose outputs you can feed in. If you don't, the long pole is the RAG pipeline, not Ragas itself.

## 3. Primitives

- **Metric** — a callable that takes a row and returns a 0-1 score. The four core RAG metrics ship out of the box, plus a growing list (answer correctness, answer similarity, context entity recall, aspect critique, etc.).
- **Dataset** — HuggingFace `Dataset` with the expected column shape.
- **Evaluate** — `ragas.evaluate(dataset, metrics)` returns a `Result` with per-row and aggregate scores.
- **LLM-judge backbone** — most metrics call an LLM under the hood (OpenAI by default; swappable via `RunConfig`). The judge prompts are baked in but inspectable in the repo.

## 4. Where it shines

- **The RAG quadrant is the moat.** Faithfulness, answer relevancy, context precision, and context recall together let you actually diagnose where a RAG pipeline is failing — model hallucination vs retriever recall vs retriever precision. Writing these yourself in Promptfoo or Braintrust takes serious effort to get right; the Ragas implementations are based on a peer-reviewed paper and are battle-tested.
- **Cheap to layer in.** It's a library, not a framework. Drop it inside your existing eval runner (LangSmith, Braintrust, a Python script) and you get the RAG metrics without abandoning whatever else you have.
- **Apache 2.0, no hosted product.** No vendor lock-in, no account, no quota.
- **Active research-aligned development.** New metrics land regularly as the RAG-eval literature evolves.

## 5. Where it bites

- **Narrow scope by design.** Not a RAG task? Ragas does almost nothing for you. The four core metrics don't map onto generation tasks, transformation tasks, classification tasks, or agentic tasks.
- **Not a framework.** No CI integration, no UI, no dataset management, no run history. You bring all of that — or pair Ragas with one of the framework-level tools in this comparison.
- **LLM-judge variability is the floor.** Most metrics are LLM-judged under the hood, so their scores carry the same noise and cost as any other LLM-judge eval.
- **API has changed across versions.** Like LangSmith, Ragas has had multiple eval-call generations; older blog posts use APIs that no longer exist. Pin a version and lock the metric prompts if you're using it in CI.
- **Cost can creep.** Per-row, each metric is one to three LLM calls. For a 500-row eval over four metrics, you're looking at 2000+ judge calls per run.

## 6. My rubric scores (DRAFT, with a structural caveat)

> Scoring methodology: [`methodology/rubric.md`](../methodology/rubric.md). The rubric is tuned for **general eval frameworks for mid-size product teams** — Ragas is a specialized metric library, so several axes are structural mismatches rather than fair comparisons. Read the verdict in §7 before reading too much into the headline number.

| Axis | Weight | Score | Reasoning |
|---|---|---|---|
| Developer ergonomics | 0.20 | **3** | `pip install` is trivial; wiring it into your runner is on you. If your task is RAG-shaped, this is a 4. If it isn't, it's irrelevant. |
| CI integration | 0.15 | **3** | It's a Python library — as good as your runner. No first-class CI story of its own. |
| Cost transparency | 0.15 | **2** | No built-in tracking; whatever your runner provides. |
| Multi-model support | 0.15 | **4** | Swappable judge LLM via `RunConfig`; usable with OpenAI, Anthropic, OSS via OpenAI-compatible endpoints. |
| Output analysis | 0.15 | **1** | No UI, no diffs, no slice analysis — it returns scores, that's it. Pair with a framework for output analysis. |
| OSS posture | 0.10 | **5** | Apache 2.0, no hosted dependency, no account required. |
| Safety / red-team | 0.10 | **1** | Out of scope; not what Ragas is for. |

**Weighted total (draft): 2.70 / 5.**

This is the lowest weighted score in the comparison, but that ranking is misleading on its own. See §7.

## 7. Where it doesn't fit our workload

Our sample workload — the resume-bullet rewriter — is a one-shot **transformation** task: weak bullet → STAR-style bullet. There is no `question`, no `retrieved_context`, no `ground_truth`. Forcing Ragas onto this would mean either:

- Renaming fields (call the bullet the "question," the expected_themes the "context") and applying only the metrics that survive the contortion — which produces numbers but tests nothing real.
- Manufacturing a contexts column from elsewhere — which tests the manufacturing logic, not Ragas.

Either path produces results that aren't honest evidence either way, so we deliberately skip the implementation. The brief stands on its own as the *"what is this tool, when would you reach for it"* answer a TPM needs.

## 8. The actually-useful verdict (read this if you're a TPM)

**Pick Ragas if:** your product is RAG-shaped (chatbot over docs, knowledge-base Q&A, search-grounded generation) AND you need to defend a "the retriever is the problem, not the model" claim — or vice versa.

**Don't pick Ragas if:** your eval need is general-purpose (transformation, classification, agentic flows, multi-turn). The rubric score above reflects this — Ragas isn't trying to compete on those axes.

**Pair Ragas with:** one of the framework-level tools (Promptfoo, Braintrust, LangSmith, Inspect) for everything that isn't a RAG metric. The honest stack for a RAG-shipping team is usually `Ragas (for the RAG quadrant) + one general framework (for everything else: red-team, CI, UI, history)`.

**Real-world failure mode this prevents:** an engineer trying to write "faithfulness" themselves in 20 lines, getting a noisy hand-rolled judge, shipping it, and the team losing trust in the metric. The Ragas implementations are not perfect, but they're at-the-state-of-the-art and reproducible.

## 9. Open questions before final scoring

- Build the smallest possible RAG pipeline (LlamaIndex over 5 markdown files) and run the full Ragas quadrant against it to validate the §4 + §5 claims hands-on, not docs-only.
- Compare Ragas's `faithfulness` to our custom faithfulness rubric on the same outputs — do they agree often enough that you'd defer to Ragas for RAG-shaped tasks?
- Re-time the "setup cost" — 1-2 hours is optimistic and assumes the RAG pipeline already exists.
