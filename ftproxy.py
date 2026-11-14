import json, os, time, urllib.request, urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

UPSTREAM = "http://127.0.0.1:1919"
MIN_TOKENS = int(os.environ.get("FT_MIN_TOKENS", "8192"))
THINKING_OFF = os.environ.get("FT_THINKING", "on").lower() == "off"
LOG = os.environ.get("FT_LOG", "proxy_log.jsonl")

class H(BaseHTTPRequestHandler):
    def _forward(self, method):
        n = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(n) if n else None
        incoming = None
        if raw and method == "POST":
            try:
                body = json.loads(raw)
                incoming = body.get("max_tokens")
                body["max_tokens"] = max(incoming or 0, MIN_TOKENS)
                body.pop("stop", None)
                if THINKING_OFF:
                    body["chat_template_kwargs"] = {"enable_thinking": False}
                raw = json.dumps(body).encode()
            except Exception as e:
                print("parse error:", e, flush=True)
        req = urllib.request.Request(UPSTREAM + self.path, data=raw, method=method, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=1800) as r:
                data, status = r.read(), r.status
        except urllib.error.HTTPError as e:
            data, status = e.read(), e.code
        if method == "POST":
            try:
                j = json.loads(data)
                ch = j["choices"][0]
                rec = {"t": time.time(), "incoming_max": incoming, "sent_max": MIN_TOKENS,
                       "finish": ch.get("finish_reason"),
                       "tokens": j.get("usage", {}).get("completion_tokens"),
                       "content_empty": not (ch["message"].get("content") or "").strip(),
                       "thinking_off": THINKING_OFF}
                open(LOG, "a").write(json.dumps(rec) + "\n")
            except Exception:
                pass
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self): self._forward("GET")
    def do_POST(self): self._forward("POST")
    def log_message(self, *a): pass

ThreadingHTTPServer(("127.0.0.1", 1920), H).serve_forever()