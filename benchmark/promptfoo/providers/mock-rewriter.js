// Mock rewriter provider — returns canned outputs so we can exercise the
// eval pipeline without making any API calls. Outputs are deterministic but
// varied across rows so some rows pass each assertion and some fail, which
// makes the pass-rate report meaningful at a glance.
//
// Routing (deterministic, based on hash of input):
//   bucket 0 → ~32-word generic-themes rewrite        (passes length, passes themes)
//   bucket 1 → ~30-word adoption/onboarding rewrite   (passes length, hits adoption/onboarding/users)
//   bucket 2 → ~16-word terse rewrite                 (fails length, hits 1 theme)
//   bucket 3 → ~48-word stuffed rewrite               (fails length on the high side)

class MockRewriter {
  id() {
    return 'mock-rewriter';
  }

  async callApi(prompt, context) {
    const input = ((context && context.vars && context.vars.input) || '').trim();
    const bucket = hash(input) % 4;

    let output;
    switch (bucket) {
      case 0:
        output =
          `Led cross-functional ${stripVerb(input)} initiative for stakeholders across the product team, ` +
          `driving measurable adoption among users and lifting downstream metrics that unblocked the broader roadmap.`;
        break;
      case 1:
        output =
          `Drove ${stripVerb(input)} rollout across four teams, improving onboarding for new users ` +
          `and increasing adoption of the supporting product workflows by a meaningful margin quarter over quarter.`;
        break;
      case 2:
        output = `Shipped ${stripVerb(input)} to the team, improving outcomes.`;
        break;
      case 3:
        output =
          `Spearheaded the end-to-end ${stripVerb(input)} program in close partnership with cross-functional stakeholders, ` +
          `engineering leadership, product managers, and downstream customer-facing teams to drive durable adoption, ` +
          `meaningfully lift user-facing metrics, and unblock several quarters of roadmap work that had stalled.`;
        break;
    }

    return { output };
  }
}

function hash(s) {
  let h = 0;
  for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) | 0;
  return Math.abs(h);
}

function stripVerb(s) {
  return s
    .replace(
      /^(helped with|worked on|did|made|built|fixed|improved|managed|ran|sold to|hit my|trained|implemented|refactored|analyzed|wrote|set up|designed|updated)\s*/i,
      ''
    )
    .toLowerCase();
}

module.exports = MockRewriter;
