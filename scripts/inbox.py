#!/usr/bin/env python3
"""
inbox.py — manage the papers/incoming → papers/library pipeline

Commands:
  list            List all PDFs in incoming (oldest first)
  next            Print the path to the next paper to process (oldest first)
  done <pdf>      Move a paper (and its .md cache) from incoming to library
"""

import sys
import shutil
from pathlib import Path

INCOMING = Path(__file__).parent.parent / "papers" / "incoming"
LIBRARY  = Path(__file__).parent.parent / "papers" / "library"


def cmd_list():
    pdfs = sorted(INCOMING.glob("*.pdf"), key=lambda p: p.stat().st_mtime)
    if not pdfs:
        print("incoming/ is empty")
        return
    print(f"{'#':<4} {'file'}")
    print("-" * 60)
    for i, p in enumerate(pdfs, 1):
        cached = "✓" if p.with_suffix(".md").exists() else " "
        print(f"{i:<4} [{cached}] {p.name}")
    print(f"\n{len(pdfs)} paper(s) waiting  (✓ = markdown cache exists)")


def cmd_next():
    pdfs = sorted(INCOMING.glob("*.pdf"), key=lambda p: p.stat().st_mtime)
    if not pdfs:
        print("incoming/ is empty")
        sys.exit(0)
    print(str(pdfs[0]))


def cmd_done(pdf_arg: str):
    src = Path(pdf_arg)
    if not src.is_absolute():
        src = INCOMING / src.name

    if not src.exists():
        print(f"error: {src} not found", file=sys.stderr)
        sys.exit(1)

    LIBRARY.mkdir(parents=True, exist_ok=True)

    moved = []
    for ext in (".pdf", ".md"):
        candidate = src.with_suffix(ext)
        if candidate.exists():
            dest = LIBRARY / candidate.name
            shutil.move(str(candidate), str(dest))
            moved.append(dest.name)

    if moved:
        print(f"moved to library/: {', '.join(moved)}")
    else:
        print("nothing to move", file=sys.stderr)
        sys.exit(1)


def usage():
    print(__doc__.strip())
    sys.exit(1)


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        usage()
    cmd = args[0]
    if cmd == "list":
        cmd_list()
    elif cmd == "next":
        cmd_next()
    elif cmd == "done" and len(args) >= 2:
        cmd_done(args[1])
    else:
        usage()
