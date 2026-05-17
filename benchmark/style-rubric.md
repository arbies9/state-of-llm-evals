# STAR-style rubric (LLM judge)

The judge sees the **original bullet** and the **rewrite**. It returns a pass/fail per rubric item, plus a one-line reason.

A rewrite **passes overall** only if it satisfies all four criteria below.

## Criteria

1. **Action-led opening.** The first word is a strong, specific action verb (Led, Built, Launched, Drove, Reduced, Increased, Shipped, Migrated, Closed, etc.). The following openers **fail**: "Helped with", "Worked on", "Was responsible for", "Assisted in", "Participated in".

2. **Concrete scope.** Names a specific artifact, system, team, audience, or surface (e.g. "the OIDC migration", "a 4-person platform team", "the onboarding flow for new SMB customers"). Vague scopes fail: "a project", "the work", "things".

3. **Specific result.** Ends with a concrete outcome — either a quantified metric (`%`, `$`, count, time delta) or a verifiable shipped state ("rolled out to all four regions", "adopted by every product team"). Vague results fail: "improved performance", "made things better", "great impact".

4. **Reads like one bullet, not a paragraph.** One sentence. No "and then…" chains. No bullet-within-a-bullet.

## Important

This rubric judges **style only**, not factual grounding. A rewrite that invents a specific metric (e.g. "cut latency 38%") **passes style** even though it fails faithfulness — that tradeoff is what the eval is designed to surface. See [`faithfulness-rubric.md`](./faithfulness-rubric.md).

## Output format

```json
{
  "criterion_1_action_led": {"pass": true, "reason": "starts with 'Led'"},
  "criterion_2_concrete_scope": {"pass": true, "reason": "names OIDC migration specifically"},
  "criterion_3_specific_result": {"pass": true, "reason": "quantified login error rate drop"},
  "criterion_4_single_bullet": {"pass": true, "reason": "one sentence"},
  "pass": true
}
```

`pass` at the top level is the AND of the four criterion passes.
