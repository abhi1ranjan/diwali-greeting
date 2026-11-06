"""Local preview server that mimics the GitHub Pages project-site path.

Usage:  python tools/serve.py [port]
Open:   http://127.0.0.1:8000/diwali-greeting/

Serves site/ under /diwali-greeting/ only, so broken relative paths show up
locally exactly as they would at https://<user>.github.io/<repository>/.
"""
import functools
import http.server
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent / "site"
BASE = "/diwali-greeting"


class Handler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        clean = path.split("?", 1)[0].split("#", 1)[0]
        if clean == BASE:
            return str(SITE / "__missing__")
        if not clean.startswith(BASE + "/"):
            return str(SITE / "__missing__")
        return super().translate_path(clean[len(BASE):] or "/")

    def do_GET(self):
        if self.path.split("?", 1)[0] == BASE:
            self.send_response(301)
            self.send_header("Location", BASE + "/")
            self.end_headers()
            return
        super().do_GET()

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, *args):
        pass


def make_server(port: int) -> http.server.ThreadingHTTPServer:
    handler = functools.partial(Handler, directory=str(SITE))
    return http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    server = make_server(port)
    print(f"Serving http://127.0.0.1:{port}{BASE}/  (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
