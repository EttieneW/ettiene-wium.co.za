"""Local + Lambda API: login, content CRUD, document export, HTML publish."""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from documents import export_bytes, load_site, write_downloads
from render import render_index

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
PUBLIC = ROOT / "public"
COOKIE = "ew_session"
SESSION_HOURS = 8
MAX_BODY = 120_000
LOGIN_WINDOW = 300
LOGIN_MAX = 8
_login_hits: list[float] = []


def _json(data: Any, status: int = 200, extra: dict[str, str] | None = None) -> tuple[int, dict[str, str], bytes]:
    headers = {
        "content-type": "application/json; charset=utf-8",
        "cache-control": "no-store",
        "x-content-type-options": "nosniff",
    }
    if extra:
        headers.update(extra)
    return status, headers, json.dumps(data).encode("utf-8")


def _creds() -> tuple[str, str, str]:
    user = os.environ.get("ADMIN_USER", "").strip()
    password = os.environ.get("ADMIN_PASSWORD", "")
    secret = os.environ.get("SESSION_SECRET", "")
    if user and password and secret:
        return user, password, secret
    local = ROOT / "config" / "admin.local.json"
    if local.is_file():
        data = json.loads(local.read_text(encoding="utf-8"))
        return str(data.get("username") or ""), str(data.get("password") or ""), str(data.get("session_secret") or "local-dev-secret")
    if os.environ.get("SITE_BUCKET"):
        import boto3

        ssm = boto3.client("ssm")
        prefix = os.environ.get("SSM_PREFIX", "/ettiene-wium-profile/admin")
        def g(name: str, decrypt: bool = True) -> str:
            return ssm.get_parameter(Name=f"{prefix}/{name}", WithDecryption=decrypt)["Parameter"]["Value"]
        return g("username", False), g("password"), g("session_secret")
    return "Ettiene.SRE", "local-dev-only", "local-dev-secret"


def _sign(msg: str, secret: str) -> str:
    return hmac.new(secret.encode(), msg.encode(), hashlib.sha256).hexdigest()


def _make_session(user: str, secret: str) -> str:
    exp = int(time.time()) + SESSION_HOURS * 3600
    nonce = secrets.token_hex(8)
    payload = f"{user}|{exp}|{nonce}"
    return payload + "|" + _sign(payload, secret)


def _parse_session(token: str, secret: str, user: str) -> bool:
    parts = token.split("|")
    if len(parts) != 4:
        return False
    payload = "|".join(parts[:3])
    if not hmac.compare_digest(parts[3], _sign(payload, secret)):
        return False
    if parts[0] != user:
        return False
    try:
        exp = int(parts[1])
    except ValueError:
        return False
    return exp >= int(time.time())


def _cookie_from_headers(headers: dict[str, str]) -> str:
    raw = headers.get("cookie") or ""
    jar = SimpleCookie()
    try:
        jar.load(raw)
    except Exception:
        return ""
    morsel = jar.get(COOKIE)
    return morsel.value if morsel else ""


def _secure_cookie() -> str:
    return "; Secure" if os.environ.get("SITE_BUCKET") else ""


def _set_cookie(token: str, clear: bool = False) -> str:
    flags = f"Path=/; HttpOnly; SameSite=Strict{_secure_cookie()}"
    if clear:
        return f"{COOKIE}=; {flags}; Max-Age=0"
    return f"{COOKIE}={token}; {flags}; Max-Age={SESSION_HOURS * 3600}"


def _origin_ok(headers: dict[str, str]) -> bool:
    origin = (headers.get("origin") or "").rstrip("/")
    if not origin:
        return True
    allowed = {
        "https://ettiene-wium.com",
        "https://www.ettiene-wium.com",
        "http://127.0.0.1:8097",
        "http://localhost:8097",
    }
    extra = os.environ.get("ALLOWED_ORIGIN", "")
    if extra:
        allowed.add(extra.rstrip("/"))
    return origin in allowed


def _rate_ok() -> bool:
    now = time.time()
    while _login_hits and _login_hits[0] < now - LOGIN_WINDOW:
        _login_hits.pop(0)
    if len(_login_hits) >= LOGIN_MAX:
        return False
    _login_hits.append(now)
    return True


def _authed(headers: dict[str, str]) -> bool:
    user, _, secret = _creds()
    return _parse_session(_cookie_from_headers(headers), secret, user)


def _load_runtime_site() -> dict[str, Any]:
    bucket = os.environ.get("SITE_BUCKET")
    if not bucket:
        return load_site(CONTENT)
    import boto3

    s3 = boto3.client("s3")

    def obj(key: str) -> dict[str, Any]:
        body = s3.get_object(Bucket=bucket, Key=key)["Body"].read()
        data = json.loads(body.decode("utf-8"))
        return data if isinstance(data, dict) else {}

    return {
        "profile": obj("content/profile.json"),
        "cover_letter": obj("content/cover-letter.json"),
        "projects": obj("content/projects.json"),
    }


def _save_site(site: dict[str, Any]) -> None:
    def dump(name: str, obj: Any) -> bytes:
        return json.dumps(obj, indent=2, ensure_ascii=False).encode("utf-8")

    profile = site.get("profile") if isinstance(site.get("profile"), dict) else {}
    cover = site.get("cover_letter") if isinstance(site.get("cover_letter"), dict) else {}
    projects = site.get("projects") if isinstance(site.get("projects"), dict) else {}
    html = render_index(site)
    files = {
        "content/profile.json": dump("profile", profile),
        "content/cover-letter.json": dump("cover", cover),
        "content/projects.json": dump("projects", projects),
        "index.html": html.encode("utf-8"),
        "404.html": html.encode("utf-8"),
    }
    tmp = Path("/tmp/profile-downloads") if os.environ.get("SITE_BUCKET") else (ROOT / "dist" / "downloads")
    names = write_downloads(site, tmp)
    for n in names:
        files[f"downloads/{n}"] = (tmp / n).read_bytes()

    bucket = os.environ.get("SITE_BUCKET")
    if bucket:
        import boto3

        s3 = boto3.client("s3")
        types = {
            ".json": "application/json; charset=utf-8",
            ".html": "text/html; charset=utf-8",
            ".pdf": "application/pdf",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        }
        for key, body in files.items():
            ext = Path(key).suffix
            s3.put_object(
                Bucket=bucket,
                Key=key,
                Body=body,
                ContentType=types.get(ext, "application/octet-stream"),
                CacheControl="no-store" if key.startswith("content/") else "public,max-age=60",
            )
        dist_id = os.environ.get("CLOUDFRONT_ID")
        if not dist_id:
            try:
                dist_id = boto3.client("ssm").get_parameter(Name="/ettiene-wium-profile/cloudfront_id")["Parameter"]["Value"]
            except Exception:
                dist_id = ""
        if dist_id:
            boto3.client("cloudfront").create_invalidation(
                DistributionId=dist_id,
                InvalidationBatch={
                    "Paths": {"Quantity": 3, "Items": ["/index.html", "/content/*", "/downloads/*"]},
                    "CallerReference": str(int(time.time())),
                },
            )
        return

    CONTENT.mkdir(parents=True, exist_ok=True)
    (CONTENT / "profile.json").write_bytes(files["content/profile.json"])
    (CONTENT / "cover-letter.json").write_bytes(files["content/cover-letter.json"])
    (CONTENT / "projects.json").write_bytes(files["content/projects.json"])
    (PUBLIC / "index.html").write_bytes(files["index.html"])
    dl = PUBLIC / "downloads"
    dl.mkdir(parents=True, exist_ok=True)
    for n in names:
        (dl / n).write_bytes(files[f"downloads/{n}"])


def _validate_site(site: Any) -> str | None:
    if not isinstance(site, dict):
        return "body must be an object"
    for key in ("profile", "cover_letter", "projects"):
        if key not in site or not isinstance(site[key], dict):
            return f"{key} object required"
    name = site["profile"].get("name")
    if not isinstance(name, str) or not name.strip():
        return "profile.name required"
    return None


def handle(method: str, path: str, headers: dict[str, str], body: bytes) -> tuple[int, dict[str, str], bytes]:
    method = method.upper()
    parsed = urlparse(path)
    route = parsed.path.rstrip("/") or "/"
    if route.startswith("/api"):
        route = route[4:] or "/"
    headers = {k.lower(): v for k, v in headers.items()}

    if method == "OPTIONS":
        return 204, {"access-control-allow-origin": headers.get("origin") or "*", "access-control-allow-credentials": "true"}, b""

    if route in ("/login",) and method == "POST":
        if not _origin_ok(headers):
            return _json({"ok": False, "error": "bad origin"}, 400)
        if not _rate_ok():
            return _json({"ok": False, "error": "too many attempts"}, 400)
        try:
            payload = json.loads(body.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            return _json({"ok": False, "error": "invalid json"}, 400)
        user, password, secret = _creds()
        got_user = str(payload.get("username") or "")
        got_pass = str(payload.get("password") or "")

        def _eq(a: str, b: str) -> bool:
            return hmac.compare_digest(hashlib.sha256(a.encode()).digest(), hashlib.sha256(b.encode()).digest())

        if not (_eq(got_user, user) and _eq(got_pass, password)):
            time.sleep(0.4)
            return _json({"ok": False, "error": "invalid credentials"}, 401)
        token = _make_session(user, secret)
        return _json({"ok": True}, 200, {"set-cookie": _set_cookie(token)})

    if route == "/logout" and method == "POST":
        return _json({"ok": True}, 200, {"set-cookie": _set_cookie("", clear=True)})

    if route == "/session" and method == "GET":
        return _json({"ok": True, "authed": _authed(headers)})

    if route == "/content" and method == "GET":
        if not _authed(headers):
            return _json({"ok": False, "error": "unauthorized"}, 401)
        return _json({"ok": True, "site": _load_runtime_site()})

    if route == "/content" and method == "PUT":
        if not _origin_ok(headers):
            return _json({"ok": False, "error": "bad origin"}, 400)
        if not _authed(headers):
            return _json({"ok": False, "error": "unauthorized"}, 401)
        if len(body) > MAX_BODY:
            return _json({"ok": False, "error": "payload too large"}, 400)
        try:
            site = json.loads(body.decode("utf-8"))
        except json.JSONDecodeError:
            return _json({"ok": False, "error": "invalid json"}, 400)
        err = _validate_site(site)
        if err:
            return _json({"ok": False, "error": err}, 400)
        _save_site(site)
        return _json({"ok": True})

    if route == "/export" and method == "GET":
        if not _authed(headers):
            return _json({"ok": False, "error": "unauthorized"}, 401)
        q = parse_qs(parsed.query)
        kind = (q.get("kind") or ["cv"])[0]
        fmt = (q.get("format") or ["pdf"])[0]
        try:
            data, filename, ctype = export_bytes(_load_runtime_site(), kind, fmt)
        except ValueError as exc:
            return _json({"ok": False, "error": str(exc)}, 400)
        return 200, {
            "content-type": ctype,
            "content-disposition": f'attachment; filename="{filename}"',
            "cache-control": "no-store",
        }, data

    return _json({"ok": False, "error": "not found"}, 400)


def lambda_handler(event: dict[str, Any], _context: Any) -> dict[str, Any]:
    rc = event.get("requestContext") or {}
    http = rc.get("http") or {}
    method = http.get("method") or event.get("httpMethod") or "GET"
    path = event.get("rawPath") or event.get("path") or "/"
    raw_q = event.get("rawQueryString") or ""
    if raw_q:
        path = path + "?" + raw_q
    headers = dict(event.get("headers") or {})
    if event.get("cookies"):
        headers["cookie"] = "; ".join(event["cookies"])
    body = event.get("body") or ""
    if event.get("isBase64Encoded"):
        raw = base64.b64decode(body)
    else:
        raw = body.encode("utf-8") if isinstance(body, str) else body
    status, hdrs, out = handle(method, path, headers, raw)
    headers_out = {k: v for k, v in hdrs.items() if k != "set-cookie"}
    cookies = [hdrs["set-cookie"]] if "set-cookie" in hdrs else []
    ctype = hdrs.get("content-type") or ""
    if "json" in ctype or ctype.startswith("text/"):
        return {"statusCode": status, "headers": headers_out, "cookies": cookies, "body": out.decode("utf-8"), "isBase64Encoded": False}
    return {
        "statusCode": status,
        "headers": headers_out,
        "cookies": cookies,
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
        if parsed.path.startswith("/api"):
            st, hd, body = handle("GET", self.path, self._headers(), b"")
            self._send(st, hd, body)
            return
        path = parsed.path
        if path in ("/", "/index.html"):
            html = render_index(load_site(CONTENT))
            self._send(200, {"content-type": "text/html; charset=utf-8"}, html.encode("utf-8"))
            return
        rel = path.lstrip("/")
        candidates = [PUBLIC / rel, ROOT / rel, CONTENT / Path(rel).name if rel.startswith("content/") else None]
        if path.startswith("/admin"):
            candidates.insert(0, PUBLIC / "admin" / "index.html" if path.rstrip("/").endswith("admin") else PUBLIC / rel)
        for cand in candidates:
            if cand and cand.is_file():
                data = cand.read_bytes()
                ctype = MIME.get(cand.suffix, "application/octet-stream")
                self._send(200, {"content-type": ctype}, data)
                return
        self._send(404, {"content-type": "text/plain"}, b"not found")


def ensure_local_admin() -> Path:
    path = ROOT / "config" / "admin.local.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.is_file():
        path.write_text(
            json.dumps(
                {
                    "username": "Ettiene.SRE",
                    "password": "local-dev-only",
                    "session_secret": secrets.token_hex(16),
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    return path


def main() -> None:
    ensure_local_admin()
    site = load_site(CONTENT)
    write_downloads(site, PUBLIC / "downloads")
    (PUBLIC / "index.html").write_text(render_index(site), encoding="utf-8")
    host, port = "127.0.0.1", int(os.environ.get("PORT") or 8097)
    httpd = ThreadingHTTPServer((host, port), DevHandler)
    print(f"Profile http://{host}:{port}  admin http://{host}:{port}/admin/")
    print("Local login: Ettiene.SRE / local-dev-only  (config/admin.local.json)")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
