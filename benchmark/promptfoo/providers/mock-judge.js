// Mock judge provider — returns a valid llm-rubric JSON response without
// calling any real model. Pass/fail is deterministic per input so the eval
// report still shows variation across rows; the verdict is NOT meaningful as
// grading (it's a wiring smoke test).

class MockJudge {
  id() {
    return 'mock-judge';
  }

  async callApi(prompt) {
    const seed = hash(String(prompt));
    const pass = seed % 5 !== 0; // ~80% pass rate
    const payload = {
      pass,
      score: pass ? 1.0 : 0.0,
      reason: pass
        ? 'mocked judge — would-be pass'
        : 'mocked judge — would-be fail (deterministic, not a real grade)',
    };
    return { output: JSON.stringify(payload) };
  }
}

function hash(s) {
  let h = 0;
  for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) | 0;
  return Math.abs(h);
}

module.exports = MockJudge;
