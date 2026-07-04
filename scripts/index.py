#!/usr/bin/env python3
"""
index.py — maintain papers/INDEX.md, the record of processed papers

Commands:
  list                          Print the current index
  add <pdf>                     Add a paper to the index (interactive prompts for missing fields)
    --title  "Full Paper Title"
    --entity paper:short-name   Remind entity name (defaults to paper:<pdf-stem-slug>)
    --url    https://...        Source URL (arXiv link, etc.)
    --topic  ml-architecture    Remind topic tag
    --notes  "one-liner"        Optional short note
"""

import sys
import re
import argparse
from pathlib import Path
from datetime import date

INDEX = Path(__file__).parent.parent / "papers" / "INDEX.md"

HEADER = """\
# Paper Index

Papers that have been fully read and memorized. Newest first.

| Date | Title | Entity | File | Topic | Source | Notes |
|------|-------|--------|------|-------|--------|-------|
"""


def _slug(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")[:60]


def _load_rows() -> list[str]:
    if not INDEX.exists():
        return []
    lines = INDEX.read_text().splitlines()
    # rows are lines starting with | after the header separator
    rows = []
    past_sep = False
    for line in lines:
        if line.startswith("|---"):
            past_sep = True
            continue
        if past_sep and line.startswith("|"):
            rows.append(line)
    return rows


def _write(rows: list[str]):
    INDEX.parent.mkdir(parents=True, exist_ok=True)
    content = HEADER + "\n".join(rows) + ("\n" if rows else "")
    INDEX.write_text(content)


def cmd_list():
    if not INDEX.exists() or not _load_rows():
        print("Index is empty — no papers processed yet.")
        return
    print(INDEX.read_text())


def cmd_add(args):
    pdf = Path(args.pdf)
    # Accept incoming/ or library/ paths — store relative to papers/
    try:
        rel = pdf.relative_to(INDEX.parent)
    except ValueError:
        rel = Path("library") / pdf.name

    stem = pdf.stem

    title = args.title or stem.replace("-", " ").title()
    entity = args.entity or f"paper:{_slug(title)}"
    url = args.url or ""
    topic = args.topic or ""
    notes = args.notes or ""
    today = date.today().isoformat()

    # Escape pipes in fields
    def esc(s): return s.replace("|", "\\|")

    title_cell = f"[{esc(title)}]({esc(url)})" if url else esc(title)
    row = f"| {today} | {title_cell} | `{esc(entity)}` | `{esc(str(rel))}` | {esc(topic)} | {esc(url)} | {esc(notes)} |"

    rows = _load_rows()
    rows.insert(0, row)  # newest first
    _write(rows)

    print(f"Added to index: {entity}")
    print(f"  Title:  {title}")
    print(f"  File:   {rel}")
    if url:
        print(f"  Source: {url}")
    print(f"\nIndex written to {INDEX}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("list", help="Print the current index")

    p_add = sub.add_parser("add", help="Add a processed paper to the index")
    p_add.add_argument("pdf", help="Path to the PDF (incoming/ or library/)")
    p_add.add_argument("--title",  help="Full paper title")
    p_add.add_argument("--entity", help="Remind entity name, e.g. paper:bert")
    p_add.add_argument("--url",    help="Source URL (arXiv, etc.)")
    p_add.add_argument("--topic",  help="Remind topic tag")
    p_add.add_argument("--notes",  help="Short one-liner note")

    args = parser.parse_args()
    if args.cmd == "list":
        cmd_list()
    elif args.cmd == "add":
        cmd_add(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
