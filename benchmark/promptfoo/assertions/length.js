// Programmatic assertion: the rewrite must be 25–40 words inclusive.
// Words = whitespace-separated tokens after trimming.

const MIN_WORDS = 25;
const MAX_WORDS = 40;

module.exports = (output) => {
  const words = String(output).trim().split(/\s+/).filter(Boolean);
  const count = words.length;
  const pass = count >= MIN_WORDS && count <= MAX_WORDS;
  return {
    pass,
    score: pass ? 1 : 0,
    reason: `length=${count} words (target ${MIN_WORDS}-${MAX_WORDS})`,
  };
};
