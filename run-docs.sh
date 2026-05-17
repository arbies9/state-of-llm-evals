#!/usr/bin/env bash
# State of LLM Evals — serve the docs as a real docs site at http://localhost:3000.
#
# Uses docsify (a tiny JS layer loaded from a CDN by index.html) to render
# the existing markdown files as a navigable site with a left sidebar,
# search, and a homepage. Static files are served by Python's stdlib
# http.server — no npm install, no build step, no accounts.
#
# Press Ctrl+C to stop.

cd "$(dirname "$0")"

echo "Starting docs site on http://localhost:3000"
echo "  Homepage (README):  http://localhost:3000/"
echo "  Tool briefs:        http://localhost:3000/#/tools/promptfoo"
echo "  Methodology:        http://localhost:3000/#/methodology/rubric"
echo
echo "Press Ctrl+C to stop."
echo

exec python3 -m http.server 3000
