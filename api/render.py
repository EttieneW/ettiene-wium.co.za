"""Render the public profile HTML from site JSON."""
from __future__ import annotations

from html import escape
from typing import Any


def h(v: Any) -> str:
    return escape(str(v), quote=True)


def _nl(text: str) -> str:
    return "<br>\n".join(h(line) for line in text.split("\n"))


def render_index(site: dict[str, Any]) -> str:
    p = site.get("profile") if isinstance(site.get("profile"), dict) else {}
    c = site.get("cover_letter") if isinstance(site.get("cover_letter"), dict) else {}
    proj = site.get("projects") if isinstance(site.get("projects"), dict) else {}
    links = p.get("links") if isinstance(p.get("links"), dict) else {}
    skills = p.get("skills") if isinstance(p.get("skills"), dict) else {}
    name = str(p.get("name") or "Ettiene Wium")
    headline = str(p.get("headline") or "Profile")
    skill_labels = [
        ("ops", "Linux / Ops"),
        ("cloud", "Cloud / IaC"),
        ("data", "Data"),
        ("backend", "Backend"),
        ("languages", "Languages"),
    ]
    skill_html = []
    for key, label in skill_labels:
        items = skills.get(key) if isinstance(skills.get(key), list) else []
        if not items:
            continue
        lis = "".join(f"<li>{h(i)}</li>" for i in items)
        skill_html.append(f"<article><h3>{h(label)}</h3><ul>{lis}</ul></article>")

    jobs_html = []
    for job in p.get("experience") if isinstance(p.get("experience"), list) else []:
        if not isinstance(job, dict):
            continue
        bullets = "".join(
            f"<li>{h(b)}</li>" for b in (job.get("bullets") if isinstance(job.get("bullets"), list) else [])
        )
        jobs_html.append(
            "<article class=\"job\">"
            f"<h3>{h(job.get('title', ''))} — {h(job.get('company', ''))}</h3>"
            f"<p class=\"meta\">{h(job.get('dates', ''))} · {h(job.get('location', ''))}</p>"
            f"<ul>{bullets}</ul></article>"
        )

    certs = "".join(f"<li>{h(c)}</li>" for c in (p.get("certs") if isinstance(p.get("certs"), list) else []))
    edu = "".join(f"<li>{h(e)}</li>" for e in (p.get("education") if isinstance(p.get("education"), list) else []))

    work_html = []
    for it in proj.get("items") if isinstance(proj.get("items"), list) else []:
        if not isinstance(it, dict):
            continue
        url = str(it.get("url") or "")
        link = f'<p><a href="{h(url)}">Open</a></p>' if url.startswith("https://") else ""
        stack = f'<p class="meta">{h(it.get("stack", ""))}</p>' if it.get("stack") else ""
        work_html.append(
            "<article>"
            f"<p class=\"meta\">{h(it.get('status', ''))} · {h(it.get('role', ''))}</p>"
            f"<h3>{h(it.get('name', ''))}</h3>{stack}"
            f"<p>{h(it.get('blurb', ''))}</p>{link}</article>"
        )

    gh = str(links.get("github") or "")
    li = str(links.get("linkedin") or "")
    email = str(p.get("email") or "")
    phone = str(p.get("phone") or "")
    cover_paras = "".join(f"<p>{_nl(para.strip())}</p>" for para in str(c.get("body") or "").split("\n\n") if para.strip())

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{h(headline)}">
  <meta name="referrer" content="strict-origin-when-cross-origin">
  <title>{h(name)} — {h(headline)}</title>
  <link rel="stylesheet" href="/assets/css/app.css">
</head>
<body>
  <a class="skip" href="#about">Skip to content</a>
  <header class="top">
    <p class="brand">{h(name)}</p>
    <nav>
      <a href="#about">About</a>
      <a href="#skills">Skills</a>
      <a href="#experience">Experience</a>
      <a href="#work">Work</a>
      <a href="#letter">Letter</a>
      <a href="#contact">Contact</a>
    </nav>
  </header>
  <main>
    <section class="hero" id="about">
      <p class="eyebrow">{h(p.get("location", ""))}</p>
      <h1>{h(headline)}</h1>
      <p class="chip">Target: junior-to-mid SRE / DevOps · globally remote · flexi hours</p>
      <div class="prose">{_nl(str(p.get("summary") or ""))}</div>
      <p class="actions">
        <a class="btn" href="/downloads/Ettiene-Wium-CV.pdf">Download CV (PDF)</a>
        <a class="btn ghost" href="/downloads/Ettiene-Wium-CV.docx">CV (DOCX)</a>
        {"<a class='btn ghost' href='" + h(gh) + "'>GitHub</a>" if gh else ""}
        {"<a class='btn ghost' href='" + h(li) + "'>LinkedIn</a>" if li else ""}
        {"<a class='btn ghost' href='mailto:" + h(email) + "'>Email</a>" if email else ""}
      </p>
    </section>
    <section id="skills">
      <h2>Skills</h2>
      <p class="lede">Grouped by domain. Kubernetes is a lab in progress — not production years.</p>
      <div class="grid">{"".join(skill_html)}</div>
    </section>
    <section id="experience">
      <h2>Experience</h2>
      {"".join(jobs_html)}
    </section>
    <section id="certs">
      <h2>Certifications</h2>
      <ul class="plain">{certs}</ul>
      <h2>Education</h2>
      <ul class="plain">{edu}</ul>
    </section>
    <section id="work">
      <h2>Selected work</h2>
      <p class="lede">{h(proj.get("lede", ""))}</p>
      <div class="grid">{"".join(work_html)}</div>
    </section>
    <section id="letter">
      <h2>{h(c.get("heading") or "Cover letter")}</h2>
      <div class="prose letter">{cover_paras}</div>
      <p class="actions">
        <a class="btn ghost" href="/downloads/Ettiene-Wium-Cover-Letter.pdf">Letter (PDF)</a>
        <a class="btn ghost" href="/downloads/Ettiene-Wium-Cover-Letter.docx">Letter (DOCX)</a>
      </p>
    </section>
    <section id="contact">
      <h2>Contact</h2>
      <p>{h(email)}{" · " + h(phone) if phone else ""}</p>
      <p class="muted">Cape Town · globally remote · SAST (UTC+2)</p>
    </section>
  </main>
  <footer>
    <p>Public profile. Editor is at <a href="/admin/">/admin</a> (private login).</p>
  </footer>
</body>
</html>
"""
