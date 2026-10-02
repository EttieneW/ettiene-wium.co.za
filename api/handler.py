"""Local static server + Lambda stub. Public site has no login API."""
from __future__ import annotations

import base64
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from documents import load_site, write_downloads
from render import render_index

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
PUBLIC = ROOT / "public"
MAX_BODY = 120_000


def _json(data: Any, status: int = 200, extra: dict[str, str] | None = None) -> tuple[int, dict[str, str], bytes]:
    headers = {
        "content-type": "application/json; charset=utf-8",
        "cache-control": "no-store",
        "x-content-type-options": "nosniff",
    }
    if extra:
        headers.update(extra)
    return status, headers, json.dumps(data).encode("utf-8")


def handle(method: str, path: str, headers: dict[str, str], body: bytes) -> tuple[int, dict[str, str], bytes]:
    return _json({"ok": False, "error": "not found"}, 404)


def lambda_handler(event: dict[str, Any], _context: Any) -> dict[str, Any]:
    rc = event.get("requestContext") or {}
    http = rc.get("http") or {}
    method = http.get("method") or event.get("httpMethod") or "GET"
    path = event.get("rawPath") or event.get("path") or "/"
    raw_q = event.get("rawQueryString") or ""
    if raw_q:
        path = path + "?" + raw_q
    headers = dict(event.get("headers") or {})
    body = event.get("body") or ""
    if event.get("isBase64Encoded"):
        raw = base64.b64decode(body)
    else:
        raw = body.encode("utf-8") if isinstance(body, str) else body
    status, hdrs, out = handle(method, path, headers, raw)
    ctype = hdrs.get("content-type") or ""
    if "json" in ctype or ctype.startswith("text/"):
        return {"statusCode": status, "headers": hdrs, "body": out.decode("utf-8"), "isBase64Encoded": False}
    return {
        "statusCode": status,
        "headers": hdrs,
        "body": base64.b64encode(out).decode("ascii"),
        "isBase64Encoded": True,
    }


MIME = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".txt": "text/plain; charset=utf-8",
    ".ico": "image/x-icon",
    ".svg": "image/svg+xml",
    ".woff2": "font/woff2",
    ".png": "image/png",
    ".webp": "image/webp",
}


class DevHandler(BaseHTTPRequestHandler):
    server_version = "EttieneProfile/1.0"

    def log_message(self, fmt: str, *args: Any) -> None:
        print("%s - %s" % (self.address_string(), fmt % args))

    def _send(self, status: int, headers: dict[str, str], body: bytes) -> None:
        self.send_response(status)
        for k, v in headers.items():
            self.send_header(k, v)
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _headers(self) -> dict[str, str]:
        return {k.lower(): v for k, v in self.headers.items()}

    def _body(self) -> bytes:
        n = int(self.headers.get("Content-Length") or 0)
        if n > MAX_BODY:
            return b""
        return self.rfile.read(n) if n else b""

    def do_OPTIONS(self) -> None:  # noqa: N802
        st, hd, body = handle("OPTIONS", self.path, self._headers(), b"")
        self._send(st, hd, body)

    def do_POST(self) -> None:  # noqa: N802
        st, hd, body = handle("POST", self.path, self._headers(), self._body())
        self._send(st, hd, body)

    def do_PUT(self) -> None:  # noqa: N802
        st, hd, body = handle("PUT", self.path, self._headers(), self._body())
        self._send(st, hd, body)

    def do_HEAD(self) -> None:  # noqa: N802
        self.do_GET()

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path
        if path.startswith("/api") or path.startswith("/admin"):
            self._send(404, {"content-type": "text/plain"}, b"not found")
            return
        if path in ("/", "/index.html"):
            html = render_index(load_site(CONTENT))
            self._send(200, {"content-type": "text/html; charset=utf-8"}, html.encode("utf-8"))
            return
        rel = path.lstrip("/")
        candidates = [PUBLIC / rel, ROOT / rel, CONTENT / Path(rel).name if rel.startswith("content/") else None]
        for cand in candidates:
            if cand and cand.is_file():
                data = cand.read_bytes()
                ctype = MIME.get(cand.suffix, "application/octet-stream")
                self._send(200, {"content-type": ctype}, data)
                return
        self._send(404, {"content-type": "text/plain"}, b"not found")


def main() -> None:
    site = load_site(CONTENT)
    write_downloads(site, PUBLIC / "downloads")
    (PUBLIC / "index.html").write_text(render_index(site), encoding="utf-8")
    host, port = "127.0.0.1", int(os.environ.get("PORT") or 8097)
    httpd = ThreadingHTTPServer((host, port), DevHandler)
    print(f"Profile http://{host}:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
