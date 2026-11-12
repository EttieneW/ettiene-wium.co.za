"""Void Signal visual CV — public one-page download."""
from __future__ import annotations

import io
from pathlib import Path
from typing import Any

from reportlab.lib.colors import Color, HexColor
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

VOID = HexColor("#03050B")
BG2 = HexColor("#0B1220")
ELEV = HexColor("#111A2C")
ELEV2 = HexColor("#182338")
INK = HexColor("#F3F6FF")
MUTED = HexColor("#9AA8C4")
FAINT = HexColor("#6D7A96")
MINT = HexColor("#3DFFC8")
MINT_SOFT = HexColor("#0A2A22")
VIOLET = HexColor("#7C6BFF")
VIOLET_SOFT = HexColor("#1A1640")
VIOLET_INK = HexColor("#C4BBFF")
HOT = HexColor("#FF4D8D")
LINE = Color(0.49, 0.71, 1.0, alpha=0.22)

W, H = A4
ML, MR = 40.0, 32.0
FONTS = False


def _fonts() -> None:
    global FONTS
    if FONTS:
        return
    d = Path(r"C:\Windows\Fonts")
    for name, fn in (
        ("UI", "segoeui.ttf"),
        ("UI-Bold", "segoeuib.ttf"),
        ("UI-Italic", "segoeuii.ttf"),
        ("Display", "georgiab.ttf"),
        ("Display-I", "georgiai.ttf"),
    ):
        pdfmetrics.registerFont(TTFont(name, str(d / fn)))
    FONTS = True


def _short_url(url: str) -> str:
    u = url.replace("https://", "").replace("http://", "").rstrip("/")
    if u.startswith("www."):
        u = u[4:]
    return u


def _sw(text: str, font: str, size: float) -> float:
    return pdfmetrics.stringWidth(text, font, size)


def wrap(text: str, font: str, size: float, max_w: float) -> list[str]:
    text = " ".join(str(text).split())
    if not text:
        return [""]
    words = text.split(" ")
    lines: list[str] = []
    cur = words[0]
    for w in words[1:]:
        trial = cur + " " + w
        if _sw(trial, font, size) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


class VoidDoc:
    def __init__(self) -> None:
        _fonts()
        self.buf = io.BytesIO()
        self.c = canvas.Canvas(self.buf, pagesize=A4)
        self.c.setTitle("Ettiene Wium — CV")
        self.c.setAuthor("Ettiene Wium")
        self.c.setSubject("Tech Lead · Senior Backend / Software Engineer")
        self.inner = W - ML - MR
        self.y = H - 32
        self.page_i = 1
        self.page_count = 1
        self._paint()

    def _paint(self) -> None:
        c = self.c
        c.setFillColor(VOID)
        c.rect(0, 0, W, H, fill=1, stroke=0)
        c.setFillColor(MINT)
        c.setFillAlpha(0.07)
        c.circle(70, H - 30, 190, fill=1, stroke=0)
        c.setFillColor(VIOLET)
        c.setFillAlpha(0.10)
        c.circle(W - 50, H - 220, 170, fill=1, stroke=0)
        c.setFillColor(HOT)
        c.setFillAlpha(0.05)
        c.circle(W * 0.45, 90, 150, fill=1, stroke=0)
        c.setFillAlpha(1)
        if self.page_i == 1:
            c.setStrokeColor(MINT)
            c.setStrokeAlpha(0.16)
            c.setLineWidth(0.9)
            c.circle(W - 78, H - 78, 64, fill=0, stroke=1)
            c.setStrokeColor(VIOLET)
            c.setStrokeAlpha(0.20)
            c.circle(W - 78, H - 78, 86, fill=0, stroke=1)
            c.setStrokeColor(HOT)
            c.setStrokeAlpha(0.12)
            c.circle(W - 78, H - 78, 48, fill=0, stroke=1)
        c.setStrokeAlpha(1)
        c.setFillAlpha(1)
        c.setFillColor(MINT)
        c.rect(0, 0, 7, H, fill=1, stroke=0)
        c.setFillColor(VIOLET)
        c.rect(W - 3, 0, 3, H, fill=1, stroke=0)

    def new_page(self) -> None:
        self._footer()
        self.c.showPage()
        self.page_i += 1
        self._paint()
        self.c.setFillColor(MINT)
        self.c.setFont("UI-Bold", 8)
        self.c.drawString(ML, H - 28, "Ettiene Wium")
        self.c.setFillColor(VIOLET)
        self.c.setFont("UI-Italic", 8)
        site = "ettiene-wium.com"
        self.c.drawString(W - MR - _sw(site, "UI-Italic", 8), H - 28, site)
        self.c.setStrokeColor(LINE)
        self.c.setStrokeAlpha(0.55)
        self.c.setLineWidth(0.5)
        self.c.line(ML, H - 34, W - MR, H - 34)
        self.c.setStrokeAlpha(1)
        self.y = H - 50

    def _footer(self) -> None:
        c = self.c
        label = f"Ettiene Wium  ·  ettiene-wium.com  ·  {self.page_i} / {self.page_count}"
        c.setFillColor(FAINT)
        c.setFont("UI", 7.5)
        c.drawString(ML, 22, label)

    def finish(self) -> bytes:
        self._footer()
        self.c.save()
        return self.buf.getvalue()

    def text(self, s: str, x: float, y: float, size: float, font: str = "UI", color=INK) -> None:
        self.c.setFillColor(color)
        self.c.setFont(font, size)
        self.c.drawString(x, y, s)

    def right(self, s: str, x_right: float, y: float, size: float, font: str = "UI", color=INK) -> None:
        self.c.setFillColor(color)
        self.c.setFont(font, size)
        self.c.drawString(x_right - _sw(s, font, size), y, s)

    def link(self, url: str, x: float, y: float, w: float, h: float) -> None:
        if url:
            self.c.linkURL(url, (x, y, x + w, y + h), relative=0)

    def round_card(self, x: float, y: float, w: float, h: float, fill=ELEV, rail=None, radius: float = 8) -> None:
        c = self.c
        c.setFillColor(fill)
        c.setStrokeColor(LINE)
        c.setStrokeAlpha(0.7)
        c.setLineWidth(0.6)
        c.roundRect(x, y, w, h, radius, fill=1, stroke=1)
        c.setStrokeAlpha(1)
        if rail is not None:
            c.setFillColor(rail)
            c.rect(x, y + 6, 3.2, h - 12, fill=1, stroke=0)

    def pill(self, text: str, x: float, y: float, fill, ink, font: str = "UI-Bold", size: float = 7.5) -> float:
        pad_x, pad_y = 7.5, 3.6
        tw = _sw(text, font, size)
        w = tw + pad_x * 2
        h = size + pad_y * 2
        self.c.setFillColor(fill)
        self.c.roundRect(x, y, w, h, h / 2, fill=1, stroke=0)
        self.c.setFillColor(ink)
        self.c.setFont(font, size)
        self.c.drawString(x + pad_x, y + pad_y + 0.4, text)
        return w

    def section(self, title: str, x: float | None = None) -> None:
        x = ML if x is None else x
        self.y -= 8
        self.text(title.upper(), x, self.y, 8, "UI-Bold", MINT)
        self.y -= 6
        self.c.setStrokeColor(MINT)
        self.c.setStrokeAlpha(0.35)
        self.c.setLineWidth(0.7)
        self.c.line(x, self.y, W - MR, self.y)
        self.c.setStrokeAlpha(1)
        self.y -= 14

    def mark(self, portrait: Path) -> None:
        cx, cy = W - 78, H - 78
        if portrait.is_file():
            from reportlab.lib.utils import ImageReader

            side = 72.0
            self.c.saveState()
            pth = self.c.beginPath()
            pth.circle(cx, cy, side / 2.0)
            self.c.clipPath(pth, stroke=0)
            self.c.drawImage(
                ImageReader(str(portrait)),
                cx - side / 2.0,
                cy - side / 2.0,
                width=side,
                height=side,
                preserveAspectRatio=True,
                mask="auto",
            )
            self.c.restoreState()
            return
        self.c.setFillColor(MINT)
        self.c.setFillAlpha(0.10)
        self.c.circle(cx, cy, 38, fill=1, stroke=0)
        self.c.setFillAlpha(1)
        ew = "EW"
        self.c.setFillColor(MINT)
        self.c.setFont("Display", 16)
        self.c.drawString(cx - _sw(ew, "Display", 16) / 2, cy - 5, ew)


def _stat(doc: VoidDoc, x: float, top: float, w: float, h: float, value: str, label: str, rail=MINT) -> None:
    y = top - h
    doc.round_card(x, y, w, h, fill=ELEV, rail=rail, radius=7)
    vw = _sw(value, "UI-Bold", 18)
    doc.text(value, x + (w - vw) / 2, y + h - 28, 18, "UI-Bold", MINT)
    lw = _sw(label, "UI-Bold", 6.8)
    doc.text(label, x + max(10, (w - lw) / 2), y + 12, 6.8, "UI-Bold", MUTED)


def _chip(doc: VoidDoc, x: float, y: float, w: float, h: float, kicker: str, body: str) -> None:
    doc.round_card(x, y, w, h, fill=BG2, rail=None, radius=6)
    doc.text(kicker, x + 10, y + h - 16, 7, "UI-Bold", MINT)
    lines = wrap(body, "UI", 8.2, w - 18)
    by = y + h - 30
    for line in lines[:2]:
        doc.text(line, x + 10, by, 8.2, "UI", INK)
        by -= 11


def build_cv_pdf_void(site: dict[str, Any]) -> bytes:
    p = site.get("profile") if isinstance(site.get("profile"), dict) else {}
    proj = site.get("projects") if isinstance(site.get("projects"), dict) else {}
    items = [x for x in (proj.get("items") if isinstance(proj.get("items"), list) else []) if isinstance(x, dict)]
    sawis = next((it for it in items if "SAWIS" in str(it.get("name") or "")), items[0] if items else {})
    indawo = next((it for it in items if "Indawo" in str(it.get("name") or "")), {})
    fleet = next((it for it in items if "fleet" in str(it.get("name") or "").lower()), {})
    homelab = next((it for it in items if "Homelab" in str(it.get("name") or "")), {})

    name = str(p.get("name") or "Ettiene Wium")
    headline = str(p.get("headline") or "")
    interest = str(p.get("interest") or "")
    links = p.get("links") if isinstance(p.get("links"), dict) else {}
    site_u = _short_url(str(links.get("portfolio") or "https://ettiene-wium.com"))
    gh = _short_url(str(links.get("github") or ""))
    li = _short_url(str(links.get("linkedin") or ""))
    email = str(p.get("email") or "")
    phone = str(p.get("phone") or "")
    site_url = str(links.get("portfolio") or "https://ettiene-wium.com")
    gh_url = str(links.get("github") or "")
    li_url = str(links.get("linkedin") or "")

    doc = VoidDoc()
    portrait = Path(__file__).resolve().parents[1] / "content" / "portrait.jpg"
    doc.mark(portrait)
    name_right = W - 170

    doc.text(name, ML, doc.y - 2, 26, "Display", MINT)
    doc.y -= 30
    if headline:
        doc.text(headline, ML, doc.y, 10.5, "UI-Bold", INK)
        doc.y -= 15
    if interest:
        doc.text(interest, ML, doc.y, 9, "UI", MINT)
        doc.y -= 14

    loc = "Cape Town  ·  globally remote  ·  SAST"
    doc.text("  ·  ".join(x for x in (loc, email, phone) if x), ML, doc.y, 7.5, "UI", FAINT)
    if email:
        doc.link("mailto:" + email, ML, doc.y - 1, min(doc.inner, name_right - ML), 10)
    doc.y -= 12
    x = ML
    for label, url in ((site_u, site_url), (gh, gh_url), (li, li_url)):
        if not label:
            continue
        tw = _sw(label, "UI-Italic", 8)
        doc.text(label, x, doc.y, 8, "UI-Italic", MINT)
        doc.link(url, x, doc.y - 1, tw, 10)
        x += tw + 12
    doc.y -= 12
    doc.text("Open to globally remote Senior and Lead backend roles", ML, doc.y, 8, "UI-Italic", VIOLET_INK)
    doc.y -= 16

    gap = 7
    plate_w = (doc.inner - gap * 3) / 4
    plate_h = 52
    top = doc.y
    stats = (
        ("8", "YEARS PRODUCTION", MINT),
        ("2M+", "MYSQL ROWS", MINT),
        ("LEAD", "SAWIS BI", VIOLET),
        ("PRO", "AWS DEVOPS", HOT),
    )
    for i, (val, lab, rail) in enumerate(stats):
        _stat(doc, ML + i * (plate_w + gap), top, plate_w, plate_h, val, lab, rail)
    doc.y = top - plate_h - 12

    chips = (
        ("MONTHLY", "Mapper to MySQL"),
        ("2M+", "Production tables"),
        ("RECOVERY", "Trace and restore"),
        ("TEAM", "PM + Sr FE + Sr BE"),
    )
    pad = 12
    chip_gap = 6
    chip_w = (doc.inner - pad * 2 - chip_gap * 3) / 4
    chip_h = 42
    header_h = 46
    card_h = pad + header_h + chip_h + 22
    top = doc.y
    yb = top - card_h
    doc.round_card(ML, yb, doc.inner, card_h, fill=ELEV, rail=MINT, radius=9)
    tx = ML + pad + 4
    ty = top - 16
    doc.text("FEATURED  ·  SAWIS BI", tx, ty, 7, "UI-Bold", MINT)
    ty -= 15
    doc.text("Tech Lead  ·  SA wine import, export, and domestic data", tx, ty, 9, "UI-Italic", VIOLET_INK)
    cy = yb + pad
    for i, (k, b) in enumerate(chips):
        _chip(doc, tx + i * (chip_w + chip_gap), cy + 14, chip_w, chip_h, k, b)
    doc.text(
        "Failed months get a traced PHP/MySQL path. 2026 domestic-data is the current annual phase.",
        tx,
        yb + 8,
        7.5,
        "UI",
        MUTED,
    )
    doc.y = yb - 12

    lead = (
        ("PLAN", "Estimate with the client"),
        ("DECIDE", "Backend and data path"),
        ("SHIP", "PHP / MySQL delivery"),
        ("COORDINATE", "PM + Sr FE + Sr BE"),
    )
    doc.text("HOW I LEAD", ML, doc.y, 8, "UI-Bold", MINT)
    doc.y -= 8
    doc.c.setStrokeColor(MINT)
    doc.c.setStrokeAlpha(0.35)
    doc.c.setLineWidth(0.7)
    doc.c.line(ML, doc.y, W - MR, doc.y)
    doc.c.setStrokeAlpha(1)
    doc.y -= 10
    lead_h = 42
    lead_gap = 6
    lead_w = (doc.inner - lead_gap * 3) / 4
    top = doc.y
    for i, (k, b) in enumerate(lead):
        _chip(doc, ML + i * (lead_w + lead_gap), top - lead_h, lead_w, lead_h, k, b)
    doc.y = top - lead_h - 8

    doc.section("Experience")
    jobs = [
        {
            "title": "Tech Lead and Senior Backend Engineer",
            "meta": "Silicon Overdrive  ·  Cape Town",
            "dates": "Apr 2022 – Present",
            "bullets": [
                "Tech Lead on SAWIS BI. Coordinate a PM, senior frontend, and senior backend. Monthly Mapper to MySQL; tables over two million rows. When a job fails I trace the data path and restore the month.",
                "Client owner for Indawo: spec through production, including a Docker restore after the on-prem host failed.",
            ],
        },
        {
            "title": "Backend / Software Engineer",
            "meta": "RogerWilco  ·  Cape Town",
            "dates": "Jun 2018 – Mar 2022",
            "bullets": [
                "Production Laravel, Symfony, and custom PHP on Ubuntu and AWS. RBAC member dashboard and live JSE graphs.",
                "Owned WordPress and Drupal modules. Production support: DNS/TLS, security reviews.",
            ],
        },
    ]
    for job in jobs:
        doc.text(job["title"], ML, doc.y, 10, "UI-Bold", INK)
        doc.right(job["dates"], W - MR, doc.y, 7.5, "UI-Italic", FAINT)
        doc.y -= 11
        doc.text(job["meta"], ML, doc.y, 8, "UI", VIOLET_INK)
        doc.y -= 12
        for b in job["bullets"]:
            lines = wrap(b, "UI", 8.5, doc.inner - 14)
            doc.text("·", ML + 1, doc.y, 10, "UI-Bold", MINT)
            for line in lines:
                doc.text(line, ML + 12, doc.y, 8.5, "UI", INK)
                doc.y -= 11
            doc.y -= 2
        doc.y -= 4

    extras = [it for it in (indawo, fleet, homelab) if it]
    if extras:
        doc.text("ALSO", ML, doc.y, 8, "UI-Bold", MINT)
        doc.y -= 6
        doc.c.setStrokeColor(MINT)
        doc.c.setStrokeAlpha(0.35)
        doc.c.setLineWidth(0.7)
        doc.c.line(ML, doc.y, W - MR, doc.y)
        doc.c.setStrokeAlpha(1)
        doc.y -= 10
        col_w = (doc.inner - 8 * (len(extras) - 1)) / max(len(extras), 1)
        top = doc.y
        max_h = 0
        for i, it in enumerate(extras):
            blurb = str(it.get("blurb") or "")
            lines = wrap(blurb, "UI", 7.5, col_w - 22)
            hgt = 44 + 11 * len(lines)
            max_h = max(max_h, hgt)
            x0 = ML + i * (col_w + 8)
            y0 = top - hgt
            rail = (MINT, VIOLET, HOT)[i % 3]
            doc.round_card(x0, y0, col_w, hgt, fill=ELEV, rail=rail, radius=7)
            doc.text(str(it.get("name") or ""), x0 + 12, top - 14, 9, "Display", INK)
            doc.text(str(it.get("role") or ""), x0 + 12, top - 26, 7, "UI-Italic", MINT)
            by = top - 38
            for line in lines:
                doc.text(line, x0 + 12, by, 7.5, "UI", INK)
                by -= 10
        doc.y = top - max_h - 12

    pills = [
        "PHP / Laravel",
        "MySQL",
        "Mapper sync",
        "Linux",
        "Docker",
        "AWS DOP-C02",
        "CodePipeline",
        "Terraform",
        "k3s homelab",
        "Cursor / Grok / Claude / Codex",
    ]
    def _pills(labels: list[str], y: float, mint_only: bool = False) -> float:
        px, py = ML, y
        for label in labels:
            tw = _sw(label, "UI-Bold", 7) + 15
            if px + tw > W - MR:
                px = ML
                py -= 18
            fill, ink = MINT_SOFT, MINT
            if not mint_only and "k3s" in label:
                fill, ink = VIOLET_SOFT, VIOLET
            doc.pill(label, px, py - 3, fill, ink, size=7)
            px += tw + 4
        return py - 22

    doc.text("STACK", ML, doc.y, 8, "UI-Bold", MINT)
    doc.y = _pills(pills, doc.y - 14)

    certs = [str(c) for c in (p.get("certs") if isinstance(p.get("certs"), list) else [])]
    if certs:
        doc.text("CERTIFICATIONS", ML, doc.y, 8, "UI-Bold", MINT)
        short = [
            "DevOps Engineer Pro (DOP-C02)",
            "AI Practitioner",
            "Solutions Architect Assoc.",
            "SysOps Assoc.",
            "Developer Assoc.",
            "Cloud Practitioner",
        ]
        doc.y = _pills(short[: len(certs)], doc.y - 14, mint_only=True)

    edu = [str(e) for e in (p.get("education") if isinstance(p.get("education"), list) else [])]
    if edu:
        doc.text("EDUCATION", ML, doc.y, 8, "UI-Bold", MINT)
        doc.y -= 14
        for e in edu[:3]:
            for line in wrap(e, "UI", 8, doc.inner):
                doc.text(line, ML, doc.y, 8, "UI", MUTED)
                doc.y -= 11
            doc.y -= 2

    return doc.finish()
