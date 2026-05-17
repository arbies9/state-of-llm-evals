# Faithfulness rubric (LLM judge, strict)

This judge catches the most common failure mode of the resume-rewriter task: **the model invents specific verifiable claims that don't appear in the input**.

The judge sees the **original bullet** and the **rewrite**. It returns pass/fail and a one-line reason.

## Fails if the rewrite invents any of these

1. **Specific numerical metrics** — percentages, dollar amounts, counts, time durations, team sizes — when no such number appears in the input. Example: input `"Fixed bugs in the API"` → rewrite `"…reducing 5xx errors by 42%"` → **fail** (42% was fabricated).
2. **Named entities** — company names, product names, technology names, frameworks, customer names, people, teams — when none appears in the input. Example: input `"Implemented authentication"` → rewrite `"…shipped Okta SSO for Salesforce integration"` → **fail** (Okta and Salesforce are fabricated).
3. **Specific dates, places, or events** not implied by the input.

## Passes if the rewrite

- Uses generic, qualitative outcomes ("reduced login errors", "improved pipeline reliability", "increased adoption across product teams") with no fabricated specifics.
- Reframes the input action more precisely, as long as the precision is implied by the input itself.
- Adds plausible *domain-appropriate* nouns (e.g. "the auth service" for a software bullet about authentication) — these are scoping aids, not fabrications.

## Why this is strict

For this task, the input bullets contain almost no facts. So this metric is almost guaranteed to **catch a real tradeoff** with [`style-rubric.md`](./style-rubric.md): rewrites that are most stylistically impressive tend to fabricate the most. That tension is the whole point of running this workload across eval tools — we want to see how each tool surfaces that tradeoff.

## Output format

```json
{
  "fabricated_metrics": {"present": false, "examples": []},
  "fabricated_entities": {"present": false, "examples": []},
  "fabricated_dates_or_events": {"present": false, "examples": []},
  "pass": true,
  "reason": "no specific metrics, names, or dates introduced"
}
```

`pass` is `true` iff none of the three `present` flags is `true`.
