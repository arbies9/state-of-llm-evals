// Load the shared dataset.jsonl and expose it to Promptfoo as test cases.
// The dataset is the canonical source — every tool implementation reads from
// it directly so the workload stays identical across frameworks.

const fs = require('fs');
const path = require('path');

const DATASET_PATH = path.resolve(__dirname, '..', 'dataset.jsonl');

module.exports = function generateTests() {
  const lines = fs
    .readFileSync(DATASET_PATH, 'utf8')
    .split('\n')
    .filter((line) => line.trim().length > 0);

  return lines.map((line) => {
    const row = JSON.parse(line);
    return {
      vars: { input: row.input },
      metadata: {
        id: row.id,
        domain: row.domain,
        expected_themes: row.expected_themes,
      },
      description: `${row.id} [${row.domain}] ${row.input}`,
    };
  });
};
