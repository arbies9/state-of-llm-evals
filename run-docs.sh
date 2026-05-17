#!/usr/bin/env bash
# State of LLM Evals — serve the docs (rendered markdown) at http://localhost:3000.
# Requires only node. No accounts, no API keys.
#
# Press Ctrl+C to stop.

cd "$(dirname "$0")"

echo "Starting markserv on http://localhost:3000 ..."
echo "  README:    http://localhost:3000/"
echo "  Tool briefs: http://localhost:3000/tools/"
echo "  Methodology: http://localhost:3000/methodology/"
echo
echo "Press Ctrl+C to stop."
echo

exec npx --yes markserv@latest -p 3000 .
