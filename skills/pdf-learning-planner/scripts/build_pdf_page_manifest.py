#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path


COMMON_BIN_DIRS = [
    Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies/bin",
]


def find_tool(name: str, env_name: str) -> str | None:
    if os.environ.get(env_name):
        return os.environ[env_name]
    found = shutil.which(name)
    if found:
        return found
    for directory in COMMON_BIN_DIRS:
        candidate = directory / name
        if candidate.exists():
            return str(candidate)
    return None


def run_text(cmd: list[str]) -> str:
    result = subprocess.run(cmd, check=True, text=True, capture_output=True)
    return result.stdout


def pdfinfo(pdf: Path) -> dict[str, str]:
    info: dict[str, str] = {}
    exe = find_tool("pdfinfo", "PDFINFO")
    if not exe:
        return info
    try:
        for line in run_text([exe, str(pdf)]).splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                info[key.strip()] = value.strip()
    except subprocess.CalledProcessError:
        return info
    return info


def parse_pages(spec: str, page_count: int | None) -> list[int]:
    pages: set[int] = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start_s, end_s = part.split("-", 1)
            start = int(start_s)
            end = int(end_s)
            pages.update(range(start, end + 1))
        else:
            pages.add(int(part))
    if page_count is not None:
        pages = {p for p in pages if 1 <= p <= page_count}
    return sorted(pages)


def render_pages(pdf: Path, pages: list[int], out_dir: Path, dpi: int) -> list[dict[str, str | int]]:
    exe = find_tool("pdftoppm", "PDFTOPPM")
    rendered: list[dict[str, str | int]] = []
    if not exe:
        return rendered
    out_dir.mkdir(parents=True, exist_ok=True)
    for page in pages:
        prefix = out_dir / f"{pdf.stem}_p{page}"
        subprocess.run(
            [exe, "-png", "-r", str(dpi), "-f", str(page), "-l", str(page), str(pdf), str(prefix)],
            check=True,
        )
        matches = sorted(out_dir.glob(f"{pdf.stem}_p{page}-*.png"))
        if matches:
            rendered.append({"page": page, "image": str(matches[-1].resolve())})
    return rendered


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a lightweight manifest for a study PDF.")
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--sample-pages", default="1-8", help="Comma/range page spec to render, e.g. 1-8,15,20.")
    parser.add_argument("--render-dir", type=Path)
    parser.add_argument("--dpi", type=int, default=180)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    pdf = args.pdf.resolve()
    info = pdfinfo(pdf)
    page_count = int(info["Pages"]) if info.get("Pages", "").isdigit() else None
    sample_pages = parse_pages(args.sample_pages, page_count)
    render_dir = args.render_dir or (pdf.parent / "_rendered_pages")
    rendered = render_pages(pdf, sample_pages, render_dir, args.dpi)

    manifest = {
        "source_pdf": str(pdf),
        "file_size_bytes": pdf.stat().st_size,
        "pdfinfo": info,
        "sample_pages": sample_pages,
        "rendered_pages": rendered,
    }

    text = json.dumps(manifest, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text)


if __name__ == "__main__":
    main()
