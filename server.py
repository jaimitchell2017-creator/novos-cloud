#!/usr/bin/env python3
import json
import time
import uuid
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

HOST = "0.0.0.0"
PORT = 8080
MAX_SESSION_SECONDS = 60 * 60

sessions = {}

class Handler(SimpleHTTPRequestHandler):
    def _json(self, status, data):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        path = urlparse(self.path).path

        if path == "/api/session/start":
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length) if length else b"{}"
            try:
                payload = json.loads(raw.decode("utf-8"))
            except Exception:
                payload = {}

            game = str(payload.get("game", "Game Test"))
            session_id = uuid.uuid4().hex[:12]
            now = time.time()

            sessions[session_id] = {
                "id": session_id,
                "game": game,
                "started": now,
                "expires": now + MAX_SESSION_SECONDS,
                "active": True,
            }

            self._json(200, {
                "ok": True,
                "session": sessions[session_id],
                "maxSeconds": MAX_SESSION_SECONDS
            })
            return

        if path == "/api/session/stop":
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length) if length else b"{}"
            try:
                payload = json.loads(raw.decode("utf-8"))
            except Exception:
                payload = {}

            session_id = payload.get("sessionId")
            session = sessions.get(session_id)

            if session:
                session["active"] = False
                session["stopped"] = time.time()

            self._json(200, {"ok": True})
            return

        self._json(404, {"ok": False, "error": "Not found"})

    def do_GET(self):
        path = urlparse(self.path).path

        if path.startswith("/api/session/"):
            session_id = path.rsplit("/", 1)[-1]
            session = sessions.get(session_id)

            if not session:
                self._json(404, {"ok": False, "error": "Session not found"})
                return

            if session["active"] and time.time() >= session["expires"]:
                session["active"] = False
                session["expired"] = True

            remaining = max(0, int(session["expires"] - time.time()))

            self._json(200, {
                "ok": True,
                "session": session,
                "remainingSeconds": remaining
            })
            return

        return super().do_GET()

print(f"NOVOS Cloud local test server")
print(f"Listening on http://localhost:{PORT}")
print(f"Maximum session length: {MAX_SESSION_SECONDS // 3600} hour")
print("Press Ctrl+C to stop.")

server = ThreadingHTTPServer((HOST, PORT), Handler)
try:
    server.serve_forever()
except KeyboardInterrupt:
    print("\nStopping NOVOS Cloud server...")
finally:
    server.server_close()
