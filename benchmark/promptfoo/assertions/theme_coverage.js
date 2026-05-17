// Programmatic assertion: the rewrite must mention at least 2 of the
// expected_themes for this row. Case-insensitive substring match — themes are
// short keywords ("users", "pipeline"), not phrases, so substring is fine.

module.exports = (output, { test }) => {
  const themes = (test.metadata && test.metadata.expected_themes) || [];
  if (themes.length === 0) {
    return { pass: false, score: 0, reason: 'no expected_themes on this row' };
  }

  const haystack = String(output).toLowerCase();
  const hit = themes.filter((t) => haystack.includes(String(t).toLowerCase()));

  const pass = hit.length >= 2;
  return {
    pass,
    score: pass ? 1 : 0,
    reason: `matched ${hit.length}/${themes.length} themes: [${hit.join(', ')}]`,
  };
};
