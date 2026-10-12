"""Void Signal visual CV. Local _test only — not the ATS download."""
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
        self.c.setTitle("Ettiene Wium — CV (local preview)")
        self.c.setAuthor("Ettiene Wium")
        self.c.setSubject("Tech Lead · Senior Backend / Software Engineer")
        self.inner = W - ML - MR
        self.y = H - 36
        self.page_i = 1
        self.page_count = 2
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
        label = f"Ettiene Wium  ·  ettiene-wium.com  ·  local preview  ·  {self.page_i} / {self.page_count}"
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
        self.y -= 6
        self.text(title.upper(), x, self.y, 8, "UI-Bold", MINT)
        self.y -= 6
        self.c.setStrokeColor(MINT)
        self.c.setStrokeAlpha(0.35)
        self.c.setLineWidth(0.7)
        self.c.line(x, self.y, W - MR, self.y)
        self.c.setStrokeAlpha(1)
        self.y -= 12


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
    c = doc.c

    # --- header ---
    doc.text(name, ML, doc.y - 4, 28, "Display", MINT)
    doc.y -= 36
    if headline:
        doc.text(headline, ML, doc.y, 11, "UI-Bold", INK)
        doc.y -= 16

    # NOW + interest
    pill_h = doc.pill("NOW", ML, doc.y - 2, HOT, HexColor("#1A0610"), "UI-Bold", 7)
    doc.text(interest, ML + pill_h + 10, doc.y, 8.5, "UI", MUTED)
    doc.y -= 18

    loc = "Cape Town  ·  globally remote  ·  SAST"
    doc.text("  ·  ".join(x for x in (loc, email, phone) if x), ML, doc.y, 8, "UI", FAINT)
    if email:
        doc.link("mailto:" + email, ML, doc.y - 1, doc.inner, 10)
    doc.y -= 13

    x = ML
    for label, url in ((site_u, site_url), (gh, gh_url), (li, li_url)):
        if not label:
            continue
        tw = _sw(label, "UI-Italic", 8.5)
        doc.text(label, x, doc.y, 8.5, "UI-Italic", MINT)
        doc.link(url, x, doc.y - 1, tw, 11)
        x += tw + 14
    doc.y -= 18

    # --- stats ---
    gap = 8
    n_stats = 4
    plate_w = (doc.inner - gap * (n_stats - 1)) / n_stats
    plate_h = 58
    top = doc.y
    stats = (
        ("8", "YEARS PRODUCTION", MINT),
        ("2M+", "MYSQL ROWS", MINT),
        ("LEAD", "SAWIS BI", VIOLET),
        ("PRO", "AWS DEVOPS", HOT),
    )
    for i, (val, lab, rail) in enumerate(stats):
        _stat(doc, ML + i * (plate_w + gap), top, plate_w, plate_h, val, lab, rail)
    doc.y = top - plate_h - 16

    # --- featured SAWIS ---
    chips = (
        ("MONTHLY", "Mapper to MySQL sync"),
        ("2M+", "Rows in production tables"),
        ("BACKEND", "Majority of the work myself"),
        ("TEAM", "PM + Senior FE + Senior BE"),
    )
    pad = 14
    chip_gap = 8
    chip_w = (doc.inner - pad * 2 - chip_gap) / 2
    chip_h = 42
    title = str(sawis.get("name") or "SAWIS BI")
    role = str(sawis.get("role") or "Tech Lead")
    outcome = "Annual feature phases. 2026 includes major domestic-data work."
    header_h = 58
    card_h = pad + header_h + chip_h * 2 + chip_gap + 22 + pad
    top = doc.y
    yb = top - card_h
    doc.round_card(ML, yb, doc.inner, card_h, fill=ELEV, rail=MINT, radius=10)
    tx = ML + pad + 4
    ty = top - 18
    doc.text("FEATURED WORK", tx, ty, 7.5, "UI-Bold", MINT)
    ty -= 18
    doc.text(title, tx, ty, 16, "Display", INK)
    ty -= 16
    doc.text(role + "  ·  SA wine import, export, and domestic data", tx, ty, 8.5, "UI-Italic", VIOLET_INK)
    cy = yb + pad + 22
    for i, (k, b) in enumerate(chips):
        col = i % 2
        row = i // 2
        cx = tx + col * (chip_w + chip_gap)
        chip_y = cy + (1 - row) * (chip_h + chip_gap)
        _chip(doc, cx, chip_y, chip_w, chip_h, k, b)
    doc.text(outcome, tx, yb + pad + 6, 8.5, "UI", MUTED)
    doc.y = yb - 14

    # --- experience ---
    doc.section("Experience")
    jobs = [
        {
            "title": "Tech Lead and Senior Backend Engineer",
            "meta": "Silicon Overdrive  ·  Cape Town",
            "dates": "Apr 2022 – Present",
            "bullets": [
                "Tech Lead on SAWIS BI. Majority of the backend. Coordinate a project manager, a senior frontend engineer, and a senior backend engineer.",
                "Own the monthly Mapper to MySQL sync. Some tables exceed two million rows. When a job fails, I trace the data path and restore it.",
                "Own client-facing planning, estimation, technical decisions, and delivery. Annual phases; 2026 includes major domestic-data work.",
                "Client owner for Indawo: spec through production, including a Docker restore after the on-prem host failed.",
            ],
        },
        {
            "title": "Backend / Software Engineer",
            "meta": "RogerWilco  ·  Cape Town",
            "dates": "Jun 2018 – Mar 2022",
            "bullets": [
                "Production backends on Ubuntu and AWS: Laravel, Symfony, custom PHP. Owned Drupal and WordPress modules.",
                "RBAC member dashboard (Global Self-Care Federation) and live JSE data graphs. Production support: compatibility, DNS/TLS, security reviews.",
            ],
        },
    ]
    for job in jobs:
        doc.y -= 2
        doc.text(job["title"], ML, doc.y, 11, "UI-Bold", INK)
        doc.right(job["dates"], W - MR, doc.y, 8, "UI-Italic", FAINT)
        doc.y -= 13
        doc.text(job["meta"], ML, doc.y, 8.5, "UI", VIOLET_INK)
        doc.y -= 14
        for b in job["bullets"]:
            lines = wrap(b, "UI", 9, doc.inner - 14)
            doc.text("·", ML + 1, doc.y, 11, "UI-Bold", MINT)
            for line in lines:
                doc.text(line, ML + 12, doc.y, 9, "UI", INK)
                doc.y -= 12
            doc.y -= 3
        doc.y -= 6

    # --- page 2 ---
    doc.new_page()
    col_gap = 14
    col_w = (doc.inner - col_gap) / 2
    left_x = ML
    right_x = ML + col_w + col_gap
    y_left = doc.y
    y_right = doc.y

    def work_card(x: float, top: float, w: float, it: dict, rail) -> float:
        title = str(it.get("name") or "")
        role = str(it.get("role") or "")
        stack = str(it.get("stack") or "")
        blurb = str(it.get("blurb") or "")
        url = str(it.get("url") or "")
        body_font, body_size = "UI", 8.5
        lines = wrap(blurb, body_font, body_size, w - 28)
        url_line = _short_url(url) if url else ""
        h = 18 + 14 + (11 if stack else 0) + 12 * len(lines) + (12 if url_line else 0) + 16
        y = top - h
        doc.round_card(x, y, w, h, fill=ELEV, rail=rail, radius=8)
        tx = x + 14
        ty = top - 18
        doc.text(title, tx, ty, 12, "Display", INK)
        ty -= 14
        doc.text(role, tx, ty, 8, "UI-Italic", MINT)
        ty -= 12
        if stack:
            for sl in wrap(stack, "UI", 7.5, w - 28)[:2]:
                doc.text(sl, tx, ty, 7.5, "UI", FAINT)
                ty -= 10
            ty -= 2
        for line in lines:
            doc.text(line, tx, ty, body_size, "UI", INK)
            ty -= 12
        if url_line:
            doc.text(url_line, tx, ty, 8, "UI-Italic", MINT)
            doc.link(url, x, y, w, h)
        return y - 10

    def kicker(x: float, y: float, title: str) -> float:
        doc.text(title.upper(), x, y, 8, "UI-Bold", MINT)
        c.setStrokeColor(MINT)
        c.setStrokeAlpha(0.35)
        c.setLineWidth(0.7)
        c.line(x, y - 5, x + col_w, y - 5)
        c.setStrokeAlpha(1)
        return y - 16

    y_left = kicker(left_x, y_left, "Also shipping")
    if indawo:
        y_left = work_card(left_x, y_left, col_w, indawo, MINT)
    if fleet:
        y_left = work_card(left_x, y_left, col_w, fleet, VIOLET)
    if homelab:
        y_left = work_card(left_x, y_left, col_w, homelab, HOT)

    delivery = p.get("delivery") if isinstance(p.get("delivery"), list) else []
    if delivery:
        y_left = kicker(left_x, y_left - 4, "How I run a client")
        box_h = 14 + 16 * len(delivery)
        yb = y_left - box_h
        doc.round_card(left_x, yb, col_w, box_h, fill=ELEV, rail=MINT, radius=8)
        ty = y_left - 16
        for step in delivery:
            doc.text("·", left_x + 12, ty, 10, "UI-Bold", MINT)
            for line in wrap(str(step), "UI", 8, col_w - 32)[:2]:
                doc.text(line, left_x + 22, ty, 8, "UI", INK)
                ty -= 12
            ty -= 2
        y_left = yb - 8

    # right column
    y_right = kicker(right_x, y_right, "Stack")
    pills = [
        "PHP / Laravel",
        "Symfony",
        "MySQL 2M+",
        "Mapper sync",
        "REST APIs",
        "Linux",
        "Docker",
        "AWS",
        "CodePipeline",
        "Terraform",
        "k3s homelab",
        "Cursor",
        "Grok",
        "Claude",
        "Codex",
    ]
    px, py = right_x, y_right
    row_h = 18
    max_x = right_x + col_w
    for label in pills:
        tw = _sw(label, "UI-Bold", 7.5) + 16
        if px + tw > max_x:
            px = right_x
            py -= row_h
        fill = MINT_SOFT if label not in ("k3s homelab",) else VIOLET_SOFT
        ink = MINT if label not in ("k3s homelab",) else VIOLET
        doc.pill(label, px, py - 4, fill, ink)
        px += tw + 5
    y_right = py - 22

    years = [
        row
        for row in (p.get("skill_years") if isinstance(p.get("skill_years"), list) else [])
        if isinstance(row, dict) and "WordPress" not in str(row.get("label") or "")
    ]
    if years:
        y_right = kicker(right_x, y_right, "Years")
        for row in years:
            val = str(row.get("years") or "")
            lab = str(row.get("label") or "")
            doc.text(val, right_x, y_right, 9, "UI-Bold", MINT)
            body = wrap(lab, "UI", 8, col_w - 50)
            for i, line in enumerate(body):
                doc.text(line, right_x + 48, y_right - i * 11, 8, "UI", INK)
            y_right -= 11 * max(len(body), 1) + 5
        y_right -= 8

    certs = [str(c) for c in (p.get("certs") if isinstance(p.get("certs"), list) else [])]
    if certs:
        y_right = kicker(right_x, y_right, "Certifications")
        hero = certs[0]
        hero_lines = wrap(hero, "UI-Bold", 8.5, col_w - 28)
        hh = 18 + 12 * len(hero_lines)
        yb = y_right - hh
        doc.round_card(right_x, yb, col_w, hh, fill=ELEV, rail=HOT, radius=7)
        ty = y_right - 16
        for line in hero_lines:
            doc.text(line, right_x + 14, ty, 8.5, "UI-Bold", INK)
            ty -= 12
        y_right = yb - 10
        for cert in certs[1:]:
            doc.text("·", right_x + 2, y_right, 9, "UI-Bold", VIOLET)
            for line in wrap(cert, "UI", 8, col_w - 16):
                doc.text(line, right_x + 12, y_right, 8, "UI", MUTED)
                y_right -= 11
            y_right -= 3
        y_right -= 6

    edu = [str(e) for e in (p.get("education") if isinstance(p.get("education"), list) else [])]
    if edu:
        y_right = kicker(right_x, y_right, "Education")
        for e in edu:
            for line in wrap(e, "UI", 8, col_w):
                doc.text(line, right_x, y_right, 8, "UI", MUTED)
                y_right -= 11
            y_right -= 4

    band_h = 56
    yb = min(y_left, y_right) - 18 - band_h
    if yb < 36:
        yb = 36
    doc.round_card(ML, yb, doc.inner, band_h, fill=ELEV2, rail=VIOLET, radius=9)
    doc.text("ettiene-wium.com", ML + 16, yb + 30, 16, "Display", MINT)
    doc.text("Portfolio  ·  selected work  ·  this CV as a visual preview", ML + 16, yb + 14, 8, "UI", MUTED)
    doc.link(site_url, ML, yb, doc.inner, band_h)

    return doc.finish()
