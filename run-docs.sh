#!/usr/bin/env bash
# State of LLM Evals — serve the docs as a real docs site at http://localhost:3000 by default.
#
# Uses docsify (a tiny JS layer loaded from a CDN by index.html) to render
# the existing markdown files as a navigable site with a left sidebar,
# search, and a homepage. Static files are served by Python's stdlib
# http.server — no npm install, no build step, no accounts.
#
# Press Ctrl+C to stop.

cd "$(dirname "$0")"

HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-3000}"
BASE_URL="http://localhost:${PORT}"

echo "Starting docs site on ${BASE_URL}"
echo "  Homepage (README):  ${BASE_URL}/"
echo "  Tool briefs:        ${BASE_URL}/#/tools/promptfoo"
echo "  Methodology:        ${BASE_URL}/#/methodology/rubric"
echo "  Interactive:        ${BASE_URL}/compare/"
echo
echo "Press Ctrl+C to stop."
echo

# HOST defaults to 127.0.0.1 for local preview only — don't serve the repo to
# the LAN unless you opt in with HOST=0.0.0.0.
exec python3 -m http.server "$PORT" --bind "$HOST"
