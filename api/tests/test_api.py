import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "api"))

from documents import build_docx, build_pdf, cv_lines, export_bytes, load_site  # noqa: E402
from handler import handle  # noqa: E402
from render import render_index  # noqa: E402


def test_site_loads():
    site = load_site(ROOT / "content")
    assert site["profile"]["name"] == "Ettiene Wium"
    assert "SRE" in site["profile"]["headline"]
    assert "cover_letter" in site


def test_pdf_and_docx_magic():
    site = load_site(ROOT / "content")
    pdf, name, ctype = export_bytes(site, "cv", "pdf")
    assert pdf.startswith(b"%PDF")
    assert name.endswith(".pdf")
    docx, name, _ = export_bytes(site, "cover", "docx")
    assert docx[:2] == b"PK"
    assert name.endswith(".docx")
    assert build_pdf(cv_lines(site)).startswith(b"%PDF")
    assert build_docx(cv_lines(site))[:2] == b"PK"


def test_render_has_https_downloads():
    html = render_index(load_site(ROOT / "content"))
    assert "Download CV (PDF)" in html
    assert "/downloads/Ettiene-Wium-CV.pdf" in html
    assert "Junior SRE" in html
    assert "k3s" in html


def test_login_and_content_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setenv("ADMIN_USER", "Ettiene.SRE")
    monkeypatch.setenv("ADMIN_PASSWORD", "test-pass")
    monkeypatch.setenv("SESSION_SECRET", "unit-test-secret")
    bad, _, body = handle("POST", "/api/login", {"origin": "http://127.0.0.1:8097"}, json.dumps({"username": "x", "password": "y"}).encode())
    assert bad == 401
    st, headers, body = handle(
        "POST",
        "/api/login",
        {"origin": "http://127.0.0.1:8097", "content-type": "application/json"},
        json.dumps({"username": "Ettiene.SRE", "password": "test-pass"}).encode(),
    )
    assert st == 200
    cookie = headers["set-cookie"]
    token = cookie.split(";")[0]
    st, _, body = handle("GET", "/api/content", {"cookie": token}, b"")
    assert st == 200
    data = json.loads(body)
    assert data["ok"] is True
    assert data["site"]["profile"]["name"] == "Ettiene Wium"
    st, _, _ = handle("GET", "/api/content", {"cookie": "ew_session=nope"}, b"")
    assert st == 401
