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
    assert "Tech Lead" in site["profile"]["headline"]
    assert "Senior Backend" in site["profile"]["headline"]
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
    assert "Tech Lead" in html
    assert "Mapper" in html
    assert "two million" in html or "2 million" in html
    assert "k3s" in html
    assert "Indawo" in html
    assert "SAWIS" in html
    assert "Laravel" in html
    assert "streaming" in html.lower()
    assert "Cursor" in html
    assert "Grok" in html
    assert "Claude" in html
    assert "Codex" in html
    assert "Years of experience" in html or "year-count" in html
    assert "<h1>Ettiene Wium</h1>" in html
    assert "/assets/favicon.svg" in html
    assert "/assets/js/motion.js" in html
    assert 'id="stage3d"' in html
    assert 'theme-color" content="#060914"' in html
    assert "atmosphere" in html
    assert "/admin" not in html
    assert "private login" not in html.lower()
    assert "Siyabonwa" not in html
    assert "Freelance AWS fleet" in html


def test_api_has_no_login():
    for method, path in (
        ("POST", "/api/login"),
        ("POST", "/api/logout"),
        ("GET", "/api/session"),
        ("GET", "/api/content"),
        ("PUT", "/api/content"),
        ("GET", "/api/export?kind=cv&format=pdf"),
    ):
        st, _, body = handle(method, path, {"origin": "https://ettiene-wium.com"}, b"{}")
        assert st == 404, path
        data = json.loads(body)
        assert data["ok"] is False
