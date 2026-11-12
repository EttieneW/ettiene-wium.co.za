import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "api"))

from documents import build_cv_pdf, build_cv_pdf_void, build_docx, build_pdf, cv_lines, export_bytes, load_site  # noqa: E402
from handler import handle  # noqa: E402
from render import render_index  # noqa: E402


def test_site_loads():
    site = load_site(ROOT / "content")
    assert site["profile"]["name"] == "Ettiene Wium"
    assert "Tech Lead" in site["profile"]["headline"]
    assert "Senior Backend" in site["profile"]["headline"]
    assert "cover_letter" in site


def test_pdf_and_docx_magic():
    from pypdf import PdfReader
    import io

    site = load_site(ROOT / "content")
    pdf, name, ctype = export_bytes(site, "cv", "pdf")
    assert pdf.startswith(b"%PDF")
    assert name.endswith(".pdf")
    assert b"Siyabonwa" not in pdf
    assert b"tf-fleet-iac" not in pdf
    text = "\n".join((p.extract_text() or "") for p in PdfReader(io.BytesIO(pdf)).pages)
    assert "ettiene-wium.com" in text
    docx, name, _ = export_bytes(site, "cover", "docx")
    assert docx[:2] == b"PK"
    assert name.endswith(".docx")
    assert build_pdf(cv_lines(site)).startswith(b"%PDF")
    assert build_docx(cv_lines(site))[:2] == b"PK"


def test_render_has_https_downloads():
    html = render_index(load_site(ROOT / "content"))
    assert "Download CV (PDF)" in html
    assert "/downloads/Ettiene-Wium-CV.pdf?v=" in html
    assert 'target="_blank"' in html
    assert html.count("/downloads/Ettiene-Wium-CV.pdf?v=") >= 2
    assert "Tech Lead" in html
    assert "PHP and MySQL" in html
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
    assert "tf-fleet-iac" not in html
    assert "github.com/EttieneW/tf-fleet" not in html
    assert 'id="letter"' not in html
    assert "Staff-track" not in html
    assert "Letter (PDF)" in html
    assert "cases-compact" in html
    assert "follow the data" in html.lower()
    assert "AWS Certified AI Practitioner" in html


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


def test_public_cv_is_void_one_pager():
    from pypdf import PdfReader
    import io

    site = load_site(ROOT / "content")
    exported, name, _ = export_bytes(site, "cv", "pdf")
    void = build_cv_pdf_void(site)
    generated = build_cv_pdf_void(site, generate=True)
    ats = build_cv_pdf(site)
    assert name.endswith(".pdf")
    assert exported.startswith(b"%PDF")
    assert void.startswith(b"%PDF")
    assert generated.startswith(b"%PDF")
    assert ats != void
    assert exported == void
    reader = PdfReader(io.BytesIO(exported))
    assert len(reader.pages) == 1
    text = "\n".join((p.extract_text() or "") for p in reader.pages).lower()
    for needle in (
        "sawis",
        "2m+",
        "mapper",
        "ettiene-wium.com",
        "tech lead",
        "indawo",
        "php",
        "mysql",
        "dop-c02",
        "ai practitioner",
        "1 / 1",
    ):
        assert needle in text, needle
    assert "siyabonwa" not in text
    assert "tf-fleet-iac" not in text
    assert "local preview" not in text
    assert "staff-track" not in text
    assert "github.com/ettienew/tf-fleet" not in text
