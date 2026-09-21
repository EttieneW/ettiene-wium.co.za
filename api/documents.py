"""Generate CV and cover-letter PDF/DOCX from site JSON. Stdlib only."""
from __future__ import annotations

import io
import zipfile
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape as xml_esc

ROOT = Path(__file__).resolve().parents[1]


def load_site(content_dir: Path | None = None) -> dict[str, Any]:
    d = content_dir or (ROOT / "content")

    def j(name: str) -> dict[str, Any]:
        import json

        p = d / name
        if not p.is_file():
            return {}
        data = json.loads(p.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}

    return {
        "profile": j("profile.json"),
        "cover_letter": j("cover-letter.json"),
        "projects": j("projects.json"),
    }


def _wrap(text: str, width: int) -> list[str]:
    lines: list[str] = []
    for para in text.replace("\r\n", "\n").split("\n"):
        words = para.split()
        if not words:
            lines.append("")
            continue
        cur = words[0]
        for w in words[1:]:
            if len(cur) + 1 + len(w) <= width:
                cur += " " + w
            else:
                lines.append(cur)
                cur = w
        lines.append(cur)
    return lines


def cv_lines(site: dict[str, Any]) -> list[tuple[str, str]]:
    """Return (style, text) rows. style in title, h1, h2, meta, body, bullet."""
    p = site.get("profile") if isinstance(site.get("profile"), dict) else {}
    rows: list[tuple[str, str]] = []
    name = str(p.get("name") or "Ettiene Wium")
    rows.append(("title", name))
    rows.append(("h1", str(p.get("headline") or "")))
    loc = str(p.get("location") or "")
    email = str(p.get("email") or "")
    phone = str(p.get("phone") or "")
    links = p.get("links") if isinstance(p.get("links"), dict) else {}
    bits = [x for x in (loc, email, phone, str(links.get("github") or ""), str(links.get("linkedin") or "")) if x]
    rows.append(("meta", "  ·  ".join(bits)))
    rows.append(("h2", "Summary"))
    for line in str(p.get("summary") or "").split("\n"):
        if line.strip():
            rows.append(("body", line.strip()))
    skills = p.get("skills") if isinstance(p.get("skills"), dict) else {}
    labels = {
        "ops": "Linux / Ops",
        "cloud": "Cloud / IaC",
        "data": "Data",
        "backend": "Backend",
        "languages": "Languages",
        "other": "Other",
    }
    years = p.get("skill_years") if isinstance(p.get("skill_years"), list) else []
    if years:
        rows.append(("h2", "Years of experience"))
        for row in years:
            if not isinstance(row, dict):
                continue
            rows.append(("body", f"{row.get('years', '')} — {row.get('label', '')}"))
    delivery = p.get("delivery") if isinstance(p.get("delivery"), list) else []
    if delivery:
        rows.append(("h2", "How I run a production client"))
        for step in delivery:
            rows.append(("bullet", str(step)))
    rows.append(("h2", "Skills"))
    for key, label in labels.items():
        items = skills.get(key) if isinstance(skills.get(key), list) else []
        if not items:
            continue
        rows.append(("body", f"{label}: " + "; ".join(str(i) for i in items)))
    rows.append(("h2", "Experience"))
    for job in p.get("experience") if isinstance(p.get("experience"), list) else []:
        if not isinstance(job, dict):
            continue
        rows.append(("h1", f"{job.get('title', '')} — {job.get('company', '')}"))
        rows.append(("meta", f"{job.get('dates', '')}  ·  {job.get('location', '')}"))
        for b in job.get("bullets") if isinstance(job.get("bullets"), list) else []:
            rows.append(("bullet", str(b)))
    rows.append(("h2", "Certifications"))
    for c in p.get("certs") if isinstance(p.get("certs"), list) else []:
        rows.append(("bullet", str(c)))
    rows.append(("h2", "Education"))
    for e in p.get("education") if isinstance(p.get("education"), list) else []:
        rows.append(("bullet", str(e)))
    proj = site.get("projects") if isinstance(site.get("projects"), dict) else {}
    items = proj.get("items") if isinstance(proj.get("items"), list) else []
    if items:
        rows.append(("h2", "Selected work"))
        for it in items:
            if not isinstance(it, dict):
                continue
            rows.append(("h1", str(it.get("name") or "")))
            meta = "  ·  ".join(x for x in (str(it.get("status") or ""), str(it.get("role") or ""), str(it.get("stack") or "")) if x)
            if meta:
                rows.append(("meta", meta))
            if it.get("blurb"):
                rows.append(("body", str(it["blurb"])))
    return [(s, t) for s, t in rows if t]


def cover_lines(site: dict[str, Any]) -> list[tuple[str, str]]:
    p = site.get("profile") if isinstance(site.get("profile"), dict) else {}
    c = site.get("cover_letter") if isinstance(site.get("cover_letter"), dict) else {}
    rows: list[tuple[str, str]] = [
        ("title", str(p.get("name") or "Ettiene Wium")),
        ("h1", str(c.get("heading") or "Cover letter")),
        ("meta", "  ·  ".join(x for x in (str(p.get("email") or ""), str(p.get("phone") or ""), str(p.get("location") or "")) if x)),
    ]
    for para in str(c.get("body") or "").split("\n\n"):
        para = para.strip()
        if para:
            rows.append(("body", para))
            rows.append(("body", ""))
    return rows


# ----- PDF (minimal Helvetica) -----
def _pdf_escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def build_pdf(rows: list[tuple[str, str]]) -> bytes:
    page_w, page_h = 595, 842
    margin = 50
    fonts = {"title": 18, "h1": 12, "h2": 12, "meta": 9, "body": 10, "bullet": 10}
    widths = {"title": 78, "h1": 88, "h2": 88, "meta": 108, "body": 95, "bullet": 90}

    pages: list[list[tuple[str, float, float, str]]] = []
    y = page_h - margin
    cur: list[tuple[str, float, float, str]] = []

    def flush() -> None:
        nonlocal cur, y
        pages.append(cur)
        cur = []
        y = page_h - margin

    for style, text in rows:
        wrap_w = widths[style]
        prefix = "- " if style == "bullet" else ""
        chunks = _wrap(prefix + text, wrap_w) or [""]
        gap = 16 if style in ("title", "h2") else 13
        for i, chunk in enumerate(chunks):
            if y < margin + 24:
                flush()
            x = margin + (12 if style == "bullet" and i else 0)
            cur.append((style, x, y, chunk))
            y -= gap
        if style == "h2":
            y -= 4
    if cur:
        pages.append(cur)
    if not pages:
        pages.append([("body", margin, page_h - margin, " ")])

    page_count = len(pages)
    first_page_id = 3
    font_id = 3 + page_count
    first_content_id = font_id + 1
    out_objs: list[bytes] = [b""]
    out_objs.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    kid_refs = " ".join(f"{first_page_id + i} 0 R" for i in range(page_count))
    out_objs.append(f"<< /Type /Pages /Kids [{kid_refs}] /Count {page_count} >>".encode())
    content_streams: list[bytes] = []
    for page in pages:
        stream_parts = ["BT", "/F1 10 Tf"]
        last_size = 10
        for style, x, ypos, chunk in page:
            size = fonts[style]
            if size != last_size:
                stream_parts.append(f"/F1 {size} Tf")
                last_size = size
            stream_parts.append(f"1 0 0 1 {x:.1f} {ypos:.1f} Tm ({_pdf_escape(chunk)}) Tj")
        stream_parts.append("ET")
        content_streams.append("\n".join(stream_parts).encode("latin-1", "replace"))
    for i in range(page_count):
        cid = first_content_id + i
        out_objs.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {page_w} {page_h}] "
            f"/Contents {cid} 0 R /Resources << /Font << /F1 {font_id} 0 R >> >> >>".encode()
        )
    out_objs.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    for stream in content_streams:
        out_objs.append(b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream")

    buf = io.BytesIO()
    buf.write(b"%PDF-1.4\n")
    offsets = [0]
    for i, obj in enumerate(out_objs[1:], start=1):
        offsets.append(buf.tell())
        buf.write(f"{i} 0 obj\n".encode())
        buf.write(obj)
        buf.write(b"\nendobj\n")
    xref = buf.tell()
    n = len(out_objs) - 1
    buf.write(f"xref\n0 {n + 1}\n".encode())
    buf.write(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        buf.write(f"{off:010d} 00000 n \n".encode())
    buf.write(f"trailer\n<< /Size {n + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
    return buf.getvalue()


# ----- DOCX (OOXML zip) -----
def _w_p(text: str, style: str | None = None, bold: bool = False, size: int | None = None) -> str:
    ppr = ""
    if style:
        ppr += f"<w:pStyle w:val=\"{style}\"/>"
    rpr = ""
    if bold:
        rpr += "<w:b/>"
    if size:
        rpr += f"<w:sz w:val=\"{size}\"/><w:szCs w:val=\"{size}\"/>"
    rpr += "<w:rFonts w:ascii=\"Calibri\" w:hAnsi=\"Calibri\"/>"
    t = xml_esc(text)
    return (
        f"<w:p><w:pPr>{ppr}</w:pPr><w:r><w:rPr>{rpr}</w:rPr>"
        f"<w:t xml:space=\"preserve\">{t}</w:t></w:r></w:p>"
    )


def build_docx(rows: list[tuple[str, str]]) -> bytes:
    body = []
    for style, text in rows:
        if style == "title":
            body.append(_w_p(text, bold=True, size=36))
        elif style == "h1":
            body.append(_w_p(text, bold=True, size=24))
        elif style == "h2":
            body.append(_w_p(text.upper(), bold=True, size=22))
        elif style == "meta":
            body.append(_w_p(text, size=18))
        elif style == "bullet":
            body.append(_w_p("• " + text, size=20))
        else:
            body.append(_w_p(text, size=20))
    document_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f"<w:body>{''.join(body)}<w:sectPr><w:pgSz w:w=\"11906\" w:h=\"16838\"/>"
        "<w:pgMar w:top=\"720\" w:right=\"720\" w:bottom=\"720\" w:left=\"720\"/></w:sectPr>"
        "</w:body></w:document>"
    )
    content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""
    rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", rels)
        z.writestr("word/document.xml", document_xml)
    return buf.getvalue()


def export_bytes(site: dict[str, Any], kind: str, fmt: str) -> tuple[bytes, str, str]:
    kind = kind.lower()
    fmt = fmt.lower()
    rows = cover_lines(site) if kind in ("cover", "cover-letter", "letter") else cv_lines(site)
    stem = "Ettiene-Wium-Cover-Letter" if kind in ("cover", "cover-letter", "letter") else "Ettiene-Wium-CV"
    if fmt == "pdf":
        return build_pdf(rows), f"{stem}.pdf", "application/pdf"
    if fmt in ("docx", "doc"):
        return build_docx(rows), f"{stem}.docx", (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    raise ValueError("format must be pdf or docx")


def write_downloads(site: dict[str, Any], dest: Path) -> list[str]:
    dest.mkdir(parents=True, exist_ok=True)
    names = []
    for kind in ("cv", "cover"):
        for fmt in ("pdf", "docx"):
            data, filename, _ = export_bytes(site, kind, fmt)
            path = dest / filename
            path.write_bytes(data)
            names.append(filename)
    return names
