#!/bin/bash
# Double-click in Finder to start trip planning.
# Starts the local server and opens the planning page in your browser.
cd "$(dirname "$0")"
exec python3 serve.py
