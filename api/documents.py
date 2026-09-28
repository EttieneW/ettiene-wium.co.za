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
        "ai": "AI tooling",
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


# ----- PDF (WinAnsi Helvetica family, stdlib only) -----
ACCENT = (0.118, 0.310, 0.290)
INK = (0.086, 0.078, 0.071)
MUTED = (0.369, 0.349, 0.325)
RULE = (0.118, 0.310, 0.290)

_WINANSI = {
    "\u2014": " - ",
    "\u2013": "-",
    "\u2011": "-",
    "\u2018": "'",
    "\u2019": "'",
    "\u201c": '"',
    "\u201d": '"',
    "\u2022": "\xb7",
    "\u00b7": "\xb7",
    "\u2192": "->",
    "\u00a0": " ",
    "\u2026": "...",
    "\u2248": "~",
}


def _winansi(s: str) -> bytes:
    for a, b in _WINANSI.items():
        s = s.replace(a, b)
    raw = s.encode("cp1252", "replace")
    return raw.replace(b"\\", b"\\\\").replace(b"(", b"\\(").replace(b")", b"\\)")


def _plain(s: str) -> str:
    for a, b in _WINANSI.items():
        s = s.replace(a, b)
    return s


def _wrap_pt(text: str, size: float, max_w: float) -> list[str]:
    text = _plain(text)
    avg = size * 0.48
    lines: list[str] = []
    for para in text.replace("\r\n", "\n").split("\n"):
        words = para.split()
        if not words:
            lines.append("")
            continue
        cur = words[0]
        for w in words[1:]:
            if (len(cur) + 1 + len(w)) * avg <= max_w:
                cur += " " + w
            else:
                lines.append(cur)
                cur = w
        lines.append(cur)
    return lines or [""]


class _Pdf:
    page_w = 595.28
    page_h = 841.89

    def __init__(self) -> None:
        self.margin = 48.0
        self.y = self.page_h - 44
        self.ops: list[str] = []
        self.pages: list[bytes] = []
        self.page_i = 1
        self._running = ""

    def set_running(self, name: str) -> None:
        self._running = name

    def _flush(self) -> None:
        if self.ops:
            self.pages.append("\n".join(self.ops).encode("latin-1", "replace"))
        self.ops = []
        self.y = self.page_h - 52
        self.page_i += 1
        if self._running:
            self._page_header()

    def need(self, h: float) -> None:
        if self.y - h < 58:
            self._flush()

    def rgb(self, c: tuple[float, float, float]) -> str:
        return f"{c[0]:.3f} {c[1]:.3f} {c[2]:.3f} rg"

    def line(self, x1: float, y1: float, x2: float, y2: float, color: tuple[float, float, float], w: float = 0.8) -> None:
        self.ops.append(
            f"{w:.2f} w {color[0]:.3f} {color[1]:.3f} {color[2]:.3f} RG {x1:.1f} {y1:.1f} m {x2:.1f} {y2:.1f} l S"
        )

    def text(self, s: str, x: float, y: float, size: float, font: str = "F1", color: tuple[float, float, float] = INK) -> None:
        lit = _winansi(_plain(s)).decode("latin-1")
        self.ops.append(
            f"BT /{font} {size:.1f} Tf {self.rgb(color)} 1 0 0 1 {x:.1f} {y:.1f} Tm ({lit}) Tj ET"
        )

    def para(self, s: str, size: float, leading: float, font: str = "F1", color: tuple[float, float, float] = INK, indent: float = 0, width: float | None = None) -> None:
        max_w = (width if width is not None else (self.page_w - 2 * self.margin)) - indent
        x = self.margin + indent
        for chunk in _wrap_pt(s, size, max_w):
            self.need(leading)
            if chunk:
                self.text(chunk, x, self.y, size, font, color)
            self.y -= leading

    def _page_header(self) -> None:
        self.text(self._running.upper(), self.margin, self.page_h - 36, 8, "F2", ACCENT)
        self.text("Curriculum Vitae", self.page_w - self.margin - 82, self.page_h - 36, 8, "F1", MUTED)
        self.line(self.margin, self.page_h - 42, self.page_w - self.margin, self.page_h - 42, ACCENT, 0.9)
        self.y = self.page_h - 58

    def section(self, title: str) -> None:
        self.need(28)
        self.y -= 8
        self.text(title.upper(), self.margin, self.y, 10, "F2", ACCENT)
        self.y -= 6
        self.line(self.margin, self.y, self.page_w - self.margin, self.y, ACCENT, 1.0)
        self.y -= 14

    def footer_and_close(self) -> bytes:
        if self.ops:
            self.pages.append("\n".join(self.ops).encode("latin-1", "replace"))
        n = len(self.pages)
        # stamp footers by rebuilding... footers baked per page at flush is easier
        page_w, page_h = self.page_w, self.page_h
        font_objs = [
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>",
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Oblique /Encoding /WinAnsiEncoding >>",
        ]
        out: list[bytes] = [b""]
        out.append(b"<< /Type /Catalog /Pages 2 0 R >>")
        page_count = n
        first_page = 3
        font0 = 3 + page_count
        first_content = font0 + 3
        kids = " ".join(f"{first_page + i} 0 R" for i in range(page_count))
        out.append(f"<< /Type /Pages /Kids [{kids}] /Count {page_count} >>".encode())
        stamped: list[bytes] = []
        for i, stream in enumerate(self.pages, start=1):
            foot = (
                f"\nBT /F1 8 Tf {self.rgb(MUTED)} 1 0 0 1 {self.margin:.1f} 28 Tm "
                f"({_winansi(self._running + '  ·  ' + str(i) + ' / ' + str(page_count)).decode('latin-1')}) Tj ET"
            ).encode("latin-1")
            stamped.append(stream + foot)
        for i in range(page_count):
            cid = first_content + i
            out.append(
                (
                    f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {page_w:.2f} {page_h:.2f}] "
                    f"/Contents {cid} 0 R /Resources << /Font << "
                    f"/F1 {font0} 0 R /F2 {font0 + 1} 0 R /F3 {font0 + 2} 0 R >> >> >>"
                ).encode()
            )
        out.extend(font_objs)
        for stream in stamped:
            out.append(b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream")
        buf = io.BytesIO()
        buf.write(b"%PDF-1.4\n")
        offsets = [0]
        for i, obj in enumerate(out[1:], start=1):
            offsets.append(buf.tell())
            buf.write(f"{i} 0 obj\n".encode())
            buf.write(obj)
            buf.write(b"\nendobj\n")
        xref = buf.tell()
        total = len(out) - 1
        buf.write(f"xref\n0 {total + 1}\n".encode())
        buf.write(b"0000000000 65535 f \n")
        for off in offsets[1:]:
            buf.write(f"{off:010d} 00000 n \n".encode())
        buf.write(f"trailer\n<< /Size {total + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
        return buf.getvalue()


def _cv_header(doc: _Pdf, p: dict[str, Any]) -> None:
    name = str(p.get("name") or "Ettiene Wium")
    doc.set_running(name)
    headline = str(p.get("headline") or "")
    interest = str(p.get("interest") or "")
    loc = str(p.get("location") or "")
    email = str(p.get("email") or "")
    phone = str(p.get("phone") or "")
    links = p.get("links") if isinstance(p.get("links"), dict) else {}
    gh = str(links.get("github") or "").replace("https://", "")
    li = str(links.get("linkedin") or "").replace("https://", "")
    cx = doc.page_w / 2
    inner = doc.page_w - 2 * doc.margin
    doc.y = doc.page_h - 52

    def center(s: str, size: float, font: str, color: tuple[float, float, float], leading: float) -> None:
        for ch in _wrap_pt(s, size, inner):
            w = len(ch) * size * 0.48
            doc.text(ch, max(doc.margin, cx - w / 2), doc.y, size, font, color)
            doc.y -= leading

    center(name.upper(), 22, "F2", ACCENT, 20)
    if headline:
        center(headline, 11, "F1", INK, 14)
    contact = "  ·  ".join(x for x in (loc, email, phone) if x)
    if contact:
        center(contact, 9, "F1", MUTED, 12)
    web = "  ·  ".join(x for x in (gh, li) if x)
    if web:
        center(web, 9, "F3", MUTED, 11)
    if interest:
        center(interest, 8, "F1", MUTED, 11)
    doc.line(doc.margin, doc.y, doc.page_w - doc.margin, doc.y, ACCENT, 1.4)
    doc.y -= 18


def build_cv_pdf(site: dict[str, Any]) -> bytes:
    p = site.get("profile") if isinstance(site.get("profile"), dict) else {}
    doc = _Pdf()
    _cv_header(doc, p)

    doc.section("Summary")
    for para in str(p.get("summary") or "").split("\n"):
        if para.strip():
            doc.para(para.strip(), 10, 13)
            doc.y -= 4

    years = p.get("skill_years") if isinstance(p.get("skill_years"), list) else []
    if years:
        doc.section("Years of experience")
        inner = doc.page_w - 2 * doc.margin
        col_w = (inner - 10) / 2
        left_x = doc.margin
        right_x = doc.margin + col_w + 10
        # pair rows
        pairs = [
            row
            for row in years
            if isinstance(row, dict) and "WordPress" not in str(row.get("label") or "")
        ]
        i = 0
        while i < len(pairs):
            row_h = 28
            doc.need(row_h)
            y0 = doc.y
            for col, row in enumerate(pairs[i : i + 2]):
                x = left_x if col == 0 else right_x
                doc.text(str(row.get("years") or ""), x, y0, 11, "F2", ACCENT)
                label = str(row.get("label") or "")
                chunks = _wrap_pt(label, 8.5, col_w - 36)
                ly = y0
                for ch in chunks[:3]:
                    doc.text(ch, x + 32, ly, 8.5, "F1", INK)
                    ly -= 11
                row_h = max(row_h, y0 - ly + 6)
            doc.y = y0 - row_h
            i += 2

    skills = p.get("skills") if isinstance(p.get("skills"), dict) else {}
    labels = [
        ("lead", "Leadership"),
        ("backend", "Backend"),
        ("data", "Data"),
        ("cloud", "Cloud"),
        ("ai", "AI tooling"),
        ("languages", "Languages"),
        ("ops", "Ops"),
        ("other", "Also"),
    ]
    doc.section("Skills")
    label_w = 88
    for key, lab in labels:
        items = skills.get(key) if isinstance(skills.get(key), list) else []
        if not items:
            continue
        body = "  ·  ".join(str(i) for i in items)
        chunks = _wrap_pt(body, 9, doc.page_w - 2 * doc.margin - label_w)
        doc.need(12 * max(len(chunks), 1) + 10)
        y0 = doc.y
        doc.text(lab, doc.margin, y0, 9, "F2", ACCENT)
        for ch in chunks:
            doc.text(ch, doc.margin + label_w, doc.y, 9, "F1", INK)
            doc.y -= 12
        doc.y -= 4

    doc.section("Experience")
    for job in p.get("experience") if isinstance(p.get("experience"), list) else []:
        if not isinstance(job, dict):
            continue
        title = str(job.get("title") or "")
        dates = str(job.get("dates") or "")
        company = str(job.get("company") or "")
        loc = str(job.get("location") or "")
        doc.need(36)
        doc.text(title, doc.margin, doc.y, 11, "F2", INK)
        dw = len(dates) * 4.4
        doc.text(dates, doc.page_w - doc.margin - dw, doc.y, 9, "F3", MUTED)
        doc.y -= 13
        doc.text("  ·  ".join(x for x in (company, loc) if x), doc.margin, doc.y, 9, "F1", MUTED)
        doc.y -= 14
        for b in job.get("bullets") if isinstance(job.get("bullets"), list) else []:
            doc.need(16)
            doc.text("\u00b7", doc.margin + 2, doc.y, 11, "F2", ACCENT)
            chunks = _wrap_pt(str(b), 9.5, doc.page_w - 2 * doc.margin - 16)
            for i, ch in enumerate(chunks):
                if i:
                    doc.need(12)
                doc.text(ch, doc.margin + 14, doc.y, 9.5, "F1", INK)
                doc.y -= 12
            doc.y -= 3
        doc.y -= 6

    proj = site.get("projects") if isinstance(site.get("projects"), dict) else {}
    items = [x for x in (proj.get("items") if isinstance(proj.get("items"), list) else []) if isinstance(x, dict)][:3]
    if items:
        doc.section("Selected work")
        for it in items:
            if not isinstance(it, dict):
                continue
            doc.need(28)
            doc.text(str(it.get("name") or ""), doc.margin, doc.y, 11, "F2", INK)
            doc.y -= 12
            meta = "  ·  ".join(
                x for x in (str(it.get("role") or ""), str(it.get("status") or ""), str(it.get("stack") or "")) if x
            )
            if meta:
                doc.para(meta, 8.5, 11, "F3", MUTED)
            outcome = str(it.get("outcome") or it.get("blurb") or "")
            if outcome:
                doc.para(outcome, 9.5, 12)
            doc.y -= 4

    certs = p.get("certs") if isinstance(p.get("certs"), list) else []
    if certs:
        doc.section("Certifications")
        for c in certs:
            doc.need(14)
            doc.text("\u00b7", doc.margin + 2, doc.y, 11, "F2", ACCENT)
            doc.text(str(c), doc.margin + 14, doc.y, 10, "F1", INK)
            doc.y -= 13

    edu = p.get("education") if isinstance(p.get("education"), list) else []
    if edu:
        doc.section("Education")
        for e in edu:
            doc.para(str(e), 10, 13)

    return doc.footer_and_close()


def build_cover_pdf(site: dict[str, Any]) -> bytes:
    p = site.get("profile") if isinstance(site.get("profile"), dict) else {}
    c = site.get("cover_letter") if isinstance(site.get("cover_letter"), dict) else {}
    doc = _Pdf()
    _cv_header(doc, p)
    heading = str(c.get("heading") or "Cover letter")
    doc.section(heading)
    for para in str(c.get("body") or "").split("\n\n"):
        para = para.strip()
        if not para:
            continue
        doc.para(para, 10.5, 15)
        doc.y -= 8
    return doc.footer_and_close()


def build_pdf(rows: list[tuple[str, str]]) -> bytes:
    """Row-based PDF used by tests; export_bytes uses the designed layouts."""
    doc = _Pdf()
    doc.set_running("Ettiene Wium")
    for style, text in rows:
        if style == "title":
            doc.text(text.upper(), doc.margin, doc.y, 18, "F2", ACCENT)
            doc.y -= 22
            doc.line(doc.margin, doc.y, doc.page_w - doc.margin, doc.y, ACCENT, 1.2)
            doc.y -= 16
        elif style == "h2":
            doc.section(text)
        elif style == "h1":
            doc.need(16)
            doc.para(text, 11, 14, "F2", INK)
        elif style == "meta":
            doc.para(text, 9, 12, "F1", MUTED)
        elif style == "bullet":
            doc.need(14)
            doc.text("\u00b7", doc.margin + 2, doc.y, 11, "F2", ACCENT)
            chunks = _wrap_pt(text, 10, doc.page_w - 2 * doc.margin - 16)
            for i, ch in enumerate(chunks):
                if i:
                    doc.need(12)
                doc.text(ch, doc.margin + 14, doc.y, 10, "F1", INK)
                doc.y -= 12
            doc.y -= 2
        else:
            doc.para(text, 10, 13)
    return doc.footer_and_close()


# ----- DOCX (OOXML zip) -----
def _w_p(text: str, style: str | None = None, bold: bool = False, size: int | None = None, color: str | None = None) -> str:
    ppr = ""
    if style:
        ppr += f"<w:pStyle w:val=\"{style}\"/>"
    rpr = ""
    if bold:
        rpr += "<w:b/>"
    if size:
        rpr += f"<w:sz w:val=\"{size}\"/><w:szCs w:val=\"{size}\"/>"
    if color:
        rpr += f"<w:color w:val=\"{color}\"/>"
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
            body.append(_w_p(text.upper(), bold=True, size=40, color="1E4F4A"))
        elif style == "h1":
            body.append(_w_p(text, bold=True, size=24, color="161412"))
        elif style == "h2":
            body.append(_w_p(text.upper(), bold=True, size=22, color="1E4F4A"))
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
        data = (
            build_cover_pdf(site)
            if kind in ("cover", "cover-letter", "letter")
            else build_cv_pdf(site)
        )
        return data, f"{stem}.pdf", "application/pdf"
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
