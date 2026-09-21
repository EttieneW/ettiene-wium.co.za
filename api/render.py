"""Render the public profile HTML from site JSON."""
from __future__ import annotations

from html import escape
from typing import Any


def h(v: Any) -> str:
    return escape(str(v), quote=True)


def _nl(text: str) -> str:
    return "<br>\n".join(h(line) for line in text.split("\n"))


def _ext(url: str, label: str, class_name: str = "btn ghost") -> str:
    return (
        f'<a class="{class_name}" href="{h(url)}" target="_blank" '
        f'rel="noopener noreferrer">{h(label)}</a>'
    )


def render_index(site: dict[str, Any]) -> str:
    p = site.get("profile") if isinstance(site.get("profile"), dict) else {}
    c = site.get("cover_letter") if isinstance(site.get("cover_letter"), dict) else {}
    proj = site.get("projects") if isinstance(site.get("projects"), dict) else {}
    links = p.get("links") if isinstance(p.get("links"), dict) else {}
    skills = p.get("skills") if isinstance(p.get("skills"), dict) else {}
    name = str(p.get("name") or "Ettiene Wium")
    headline = str(p.get("headline") or "Profile")
    location = str(p.get("location") or "")
    skill_labels = [
        ("ops", "Linux / Ops"),
        ("cloud", "Cloud / IaC"),
        ("data", "Data"),
        ("backend", "Backend"),
        ("languages", "Languages"),
        ("other", "Also"),
    ]
    skill_html = []
    for key, label in skill_labels:
        items = skills.get(key) if isinstance(skills.get(key), list) else []
        if not items:
            continue
        chips = "".join(f"<li>{h(i)}</li>" for i in items)
        skill_html.append(
            f'<article class="skill-card"><h3>{h(label)}</h3><ul class="chips">{chips}</ul></article>'
        )

    jobs_html = []
    for job in p.get("experience") if isinstance(p.get("experience"), list) else []:
        if not isinstance(job, dict):
            continue
        bullets = "".join(
            f"<li>{h(b)}</li>" for b in (job.get("bullets") if isinstance(job.get("bullets"), list) else [])
        )
        jobs_html.append(
            '<article class="job">'
            f'<p class="job-when">{h(job.get("dates", ""))}</p>'
            '<div class="job-body">'
            f"<h3>{h(job.get('company', ''))}</h3>"
            f'<p class="job-title">{h(job.get("title", ""))}</p>'
            f'<p class="meta">{h(job.get("location", ""))}</p>'
            f"<ul>{bullets}</ul></div></article>"
        )

    certs = "".join(
        f"<li>{h(item)}</li>" for item in (p.get("certs") if isinstance(p.get("certs"), list) else [])
    )
    edu = "".join(
        f"<li>{h(item)}</li>" for item in (p.get("education") if isinstance(p.get("education"), list) else [])
    )

    work_html = []
    for it in proj.get("items") if isinstance(proj.get("items"), list) else []:
        if not isinstance(it, dict):
            continue
        url = str(it.get("url") or "")
        link = (
            f'<a class="text-link" href="{h(url)}" target="_blank" rel="noopener noreferrer">View</a>'
            if url.startswith("https://")
            else ""
        )
        stack = f'<p class="meta">{h(it.get("stack", ""))}</p>' if it.get("stack") else ""
        work_html.append(
            '<article class="work-card">'
            f'<p class="pill">{h(it.get("status", ""))}</p>'
            f"<h3>{h(it.get('name', ''))}</h3>"
            f'<p class="meta">{h(it.get("role", ""))}</p>{stack}'
            f"<p>{h(it.get('blurb', ''))}</p>{link}</article>"
        )

    years_html = []
    for row in p.get("skill_years") if isinstance(p.get("skill_years"), list) else []:
        if not isinstance(row, dict):
            continue
        years_html.append(
            "<li>"
            f'<span class="year-count">{h(row.get("years", ""))}</span>'
            f'<span class="year-label">{h(row.get("label", ""))}</span>'
            "</li>"
        )
    years_block = (
        f'<ol class="years">{"".join(years_html)}</ol>' if years_html else ""
    )
    steps = p.get("delivery") if isinstance(p.get("delivery"), list) else []
    steps_html = "".join(f"<li>{h(s)}</li>" for s in steps if str(s).strip())
    steps_block = (
        f'<ol class="process">{steps_html}</ol>' if steps_html else ""
    )
    hired = str(p.get("hired_for") or "")
    leaning = str(p.get("leaning_into") or "")
    split_block = ""
    if hired or leaning:
        split_block = (
            '<div class="path-grid">'
            + (
                f'<article class="path-card"><p class="kicker">Hired for</p><p>{h(hired)}</p></article>'
                if hired
                else ""
            )
            + (
                f'<article class="path-card"><p class="kicker">Leaning into</p><p>{h(leaning)}</p></article>'
                if leaning
                else ""
            )
            + "</div>"
        )
    interest = str(p.get("interest") or "")
    status_line = str(p.get("status_line") or "Open to PHP production roles and SRE / DevOps · globally remote · flexi hours")

    gh = str(links.get("github") or "")
    li = str(links.get("linkedin") or "")
    email = str(p.get("email") or "")
    phone = str(p.get("phone") or "")
    cover_paras = "".join(
        f"<p>{_nl(para.strip())}</p>" for para in str(c.get("body") or "").split("\n\n") if para.strip()
    )
    gh_btn = _ext(gh, "GitHub") if gh else ""
    li_btn = _ext(li, "LinkedIn") if li else ""
    mail_btn = f'<a class="btn ghost" href="mailto:{h(email)}">Email</a>' if email else ""
    mail_big = (
        f'<a class="contact-email" href="mailto:{h(email)}">{h(email)}</a>' if email else ""
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{h(headline)}">
  <meta name="referrer" content="strict-origin-when-cross-origin">
  <meta name="theme-color" content="#f3efe6" media="(prefers-color-scheme: light)">
  <meta name="theme-color" content="#121110" media="(prefers-color-scheme: dark)">
  <meta property="og:title" content="{h(name)} — {h(headline)}">
  <meta property="og:description" content="{h(headline)}">
  <meta property="og:url" content="https://ettiene-wium.com">
  <meta property="og:type" content="profile">
  <title>{h(name)} — {h(headline)}</title>
  <link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="/assets/css/app.css">
</head>
<body>
  <a class="skip" href="#about">Skip to content</a>
  <header class="top">
    <div class="top-inner">
      <a class="brand" href="#about">
        <img src="/assets/favicon.svg" width="28" height="28" alt="">
        <span>{h(name)}</span>
      </a>
      <nav>
        <a href="#about">About</a>
        <a href="#skills">Skills</a>
        <a href="#experience">Experience</a>
        <a href="#certs">Certs</a>
        <a href="#work">Work</a>
        <a href="#letter">Letter</a>
        <a href="#contact">Contact</a>
      </nav>
      <a class="btn btn-sm" href="/downloads/Ettiene-Wium-CV.pdf">Download CV</a>
    </div>
  </header>
  <main>
    <section class="hero" id="about">
      <p class="kicker">{h(location)}</p>
      <h1>{h(name)}</h1>
      <p class="role">{h(headline)}</p>
      {"<p class='interest'>" + h(interest) + "</p>" if interest else ""}
      <p class="status"><span class="status-dot"></span> {h(status_line)}</p>
      {split_block}
      <div class="prose">{_nl(str(p.get("summary") or ""))}</div>
      <p class="actions">
        <a class="btn" href="/downloads/Ettiene-Wium-CV.pdf">Download CV (PDF)</a>
        <a class="btn ghost" href="/downloads/Ettiene-Wium-CV.docx">CV (DOCX)</a>
        {gh_btn}
        {li_btn}
        {mail_btn}
      </p>
    </section>
    <section id="skills">
      <div class="section-head">
        <p class="section-index">01</p>
        <h2>Skills</h2>
      </div>
      <p class="lede">Years are honest. Kubernetes is homelab. AWS at work is using existing accounts.</p>
      {years_block}
      {("<h3 class='kicker'>How I run a production client</h3>" + steps_block) if steps_block else ""}
      <div class="grid">{"".join(skill_html)}</div>
    </section>
    <section id="experience">
      <div class="section-head">
        <p class="section-index">02</p>
        <h2>Experience</h2>
      </div>
      <div class="timeline">{"".join(jobs_html)}</div>
    </section>
    <section id="certs">
      <div class="section-head">
        <p class="section-index">03</p>
        <h2>Certifications and education</h2>
      </div>
      <div class="split">
        <div>
          <h3 class="kicker">AWS certifications</h3>
          <ul class="cert-list">{certs}</ul>
        </div>
        <div>
          <h3 class="kicker">Education</h3>
          <ul class="edu-list">{edu}</ul>
        </div>
      </div>
    </section>
    <section id="work">
      <div class="section-head">
        <p class="section-index">04</p>
        <h2>Selected work</h2>
      </div>
      <p class="lede">{h(proj.get("lede", ""))}</p>
      <div class="grid">{"".join(work_html)}</div>
    </section>
    <section id="letter">
      <div class="section-head">
        <p class="section-index">05</p>
        <h2>{h(c.get("heading") or "Cover letter")}</h2>
      </div>
      <div class="letter-wrap">
        <div class="letter">{cover_paras}</div>
        <p class="actions">
          <a class="btn ghost" href="/downloads/Ettiene-Wium-Cover-Letter.pdf">Letter (PDF)</a>
          <a class="btn ghost" href="/downloads/Ettiene-Wium-Cover-Letter.docx">Letter (DOCX)</a>
        </p>
      </div>
    </section>
    <section id="contact">
      <div class="section-head">
        <p class="section-index">06</p>
        <h2>Contact</h2>
      </div>
      <div class="contact-panel">
        {mail_big}
        {"<p class='phone'>" + h(phone) + "</p>" if phone else ""}
        <p class="muted">{h(location)}</p>
        <p class="actions">
          {mail_btn}
          {li_btn}
          {gh_btn}
        </p>
      </div>
    </section>
  </main>
  <footer>
    <p>Public profile. Editor is at <a href="/admin/">/admin</a> (private login).</p>
  </footer>
</body>
</html>
"""
