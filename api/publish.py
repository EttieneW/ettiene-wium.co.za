"""Write dist/ for S3: HTML, assets, content JSON, CV/letter downloads."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from documents import load_site, write_downloads
from render import render_index

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    site = load_site(ROOT / "content")
    dist = ROOT / "dist"
    if dist.exists():
        shutil.rmtree(dist)
    dist.mkdir()
    html = render_index(site)
    (dist / "index.html").write_text(html, encoding="utf-8")
    (dist / "404.html").write_text(html, encoding="utf-8")
    shutil.copytree(ROOT / "public" / "assets", dist / "assets")
    shutil.copy2(ROOT / "public" / "robots.txt", dist / "robots.txt")
    shutil.copytree(ROOT / "public" / "admin", dist / "admin")
    content = dist / "content"
    content.mkdir()
    for name in ("profile.json", "cover-letter.json", "projects.json"):
        shutil.copy2(ROOT / "content" / name, content / name)
    names = write_downloads(site, dist / "downloads")
    print("dist ready:", ", ".join(names))


if __name__ == "__main__":
    main()
