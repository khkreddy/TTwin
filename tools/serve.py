#!/usr/bin/env python3
"""Local TeacherTwin server: static files + optional Kimi K3 proxy.

Usage:
  python3 tools/serve.py
  # open http://127.0.0.1:8766/

The GitHub Pages site is static. Browser calls to api.moonshot.ai may be
blocked by CORS; this proxy exists so ISO-GEN / prompt inference can be
tested locally. The API key is sent as header X-Kimi-Key and is never written
to disk by this process.
"""
from __future__ import annotations

import json
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MOONSHOT = "https://api.moonshot.ai/v1/chat/completions"
PORT = int(__import__("os").environ.get("TTWIN_PORT", "8766"))


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def do_OPTIONS(self):
        path = self.path.rstrip("/")
        if path in ("/kimi", "/solution"):
            self.send_response(204)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Kimi-Key")
            self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
            self.end_headers()
            return
        self.send_error(404)

    def do_POST(self):
        path = self.path.rstrip("/")
        if path == "/solution":
            self._save_solution()
            return
        if path != "/kimi":
            self.send_error(404)
            return
        n = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(n)
        key = (self.headers.get("X-Kimi-Key") or "").strip()
        if not key:
            self._json(401, {"error": "missing X-Kimi-Key"})
            return
        req = urllib.request.Request(
            MOONSHOT,
            data=raw,
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                body = r.read()
                self.send_response(r.status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
        except Exception as ex:
            self._json(502, {"error": str(ex)[:400]})

    def _save_solution(self):
        n = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(n)
        try:
            rec = json.loads(raw.decode("utf-8"))
        except Exception:
            self._json(400, {"error": "invalid json"})
            return
        uid = rec.get("item_uid")
        if not uid:
            self._json(400, {"error": "missing item_uid"})
            return
        rec.setdefault("schema", "awm.solution_analysis.v1")
        sol = ROOT / "data" / "solutions"
        sol.mkdir(parents=True, exist_ok=True)
        jsonl = sol / "items.jsonl"
        with jsonl.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False, separators=(",", ":")) + "\n")
        by = {}
        if jsonl.is_file():
            for line in jsonl.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except Exception:
                    continue
                u = row.get("item_uid")
                if u:
                    by[u] = row
        index = {
            "schema": "ttwin.solutions.v1",
            "n": len(by),
            "by_uid": by,
        }
        (sol / "index.json").write_text(
            json.dumps(index, ensure_ascii=False, separators=(",", ":")) + "\n",
            encoding="utf-8",
        )
        self._json(200, {"ok": True, "item_uid": uid, "n": len(by)})

    def _json(self, code: int, obj: dict):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print(self.address_string(), "-", fmt % args)


def main() -> int:
    httpd = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"TeacherTwin  http://127.0.0.1:{PORT}/")
    httpd.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
