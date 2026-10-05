"""Standalone API & Web server for minimal-demo."""
from __future__ import annotations

import http.server
import json
import os
from pathlib import Path

PORT = int(os.environ.get("PORT", 8090))
APP_DIR = Path(__file__).resolve().parent
WEB_DIR = APP_DIR / "web"


class AppHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)

    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "app": "minimal-demo"}).encode())
            return
        elif self.path == "/api/stats":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"app": "minimal-demo", "status": "online", "port": PORT}).encode())
            return
        return super().do_GET()


def run():
    server = http.server.ThreadingHTTPServer(("0.0.0.0", PORT), AppHandler)
    print(f"[minimal-demo] Running on http://127.0.0.1:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    run()
