#!/usr/bin/env python3
"""
Local dev server for the Sabbatical trip site.

- Serves the static site in ./site (the mobile trip guide + the planning page).
- Backs the planning page's autosave: POST /api/notes writes the JSON body to
  site/data/planning-notes.json, the file Claude reads to fold notes into the trip.

    python3 serve.py [port] [--no-open]   # default port 8000, opens planning page

      planning: http://localhost:8000/plan.html   (type free-form notes; autosaves)
      guide:    http://localhost:8000/            (the mobile trip guide)

On the portal the site is static; this little write-back server only runs on the
laptop, which is where planning happens.
"""
import json
import os
import sys
import threading
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(HERE, "site")
NOTES = os.path.join(SITE, "data", "planning-notes.json")
args = [a for a in sys.argv[1:] if not a.startswith("-")]
PORT = int(args[0]) if args else 8000
OPEN = "--no-open" not in sys.argv


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=SITE, **kwargs)

    def do_POST(self):
        if self.path.rstrip("/") != "/api/notes":
            self.send_error(404, "Not found")
            return
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            data = json.loads(raw or b"{}")
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
            return
        os.makedirs(os.path.dirname(NOTES), exist_ok=True)
        with open(NOTES, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, sort_keys=True)
            f.write("\n")
        body = b'{"ok":true}'
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def end_headers(self):
        # No-cache in dev so regenerated data / edits show up immediately.
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


if __name__ == "__main__":
    plan_url = f"http://localhost:{PORT}/plan.html"
    print("\n  Sabbatical planning is running.\n")
    print(f"    ✏️  Plan (type here):  {plan_url}")
    print(f"    🗺️  Trip guide:        http://localhost:{PORT}/")
    print(f"    💾 Notes saved to:    {NOTES}")
    print("\n  Leave this open while you plan. Press Ctrl+C to stop.\n")
    if OPEN:
        threading.Timer(0.6, lambda: webbrowser.open(plan_url)).start()
    try:
        HTTPServer(("", PORT), Handler).serve_forever()
    except KeyboardInterrupt:
        print("\n  Stopped. Notes are saved.\n")
