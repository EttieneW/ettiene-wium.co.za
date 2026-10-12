"""Write a local Void Signal _test CV. Does not replace the ATS download."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "api"))

from documents import build_cv_pdf_void, load_site  # noqa: E402


def main() -> None:
    site = load_site(ROOT / "content")
    pdf = build_cv_pdf_void(site)
    dests = [
        Path.home() / "Documents" / "Ettiene-Wium-CV_test.pdf",
        ROOT / "_local" / "Ettiene-Wium-CV_test.pdf",
    ]
    for path in dests:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(pdf)
        print(path, len(pdf))


if __name__ == "__main__":
    main()
