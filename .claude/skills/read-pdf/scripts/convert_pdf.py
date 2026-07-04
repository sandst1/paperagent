#!/usr/bin/env python3
"""
Convert a PDF file to markdown using pymupdf4llm with enhanced layout analysis.
Automatically manages virtual environment and dependencies.
"""

import argparse
import subprocess
import sys
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent.resolve()
SKILL_DIR = SCRIPT_DIR.parent
VENV_DIR = SKILL_DIR / ".venv"
VENV_PYTHON = VENV_DIR / "bin" / "python"

# Required packages
PACKAGES = ["pymupdf4llm", "pymupdf-layout"]


def ensure_venv():
    """Create virtual environment if it doesn't exist."""
    if not VENV_DIR.exists():
        print(f"Creating virtual environment at {VENV_DIR}...", file=sys.stderr)
        subprocess.run([sys.executable, "-m", "venv", str(VENV_DIR)], check=True)
        print("Virtual environment created.", file=sys.stderr)


def ensure_packages():
    """Install required packages if not already installed."""
    # Check if packages are installed
    result = subprocess.run(
        [str(VENV_PYTHON), "-c", "import pymupdf4llm; import pymupdf.layout"],
        capture_output=True
    )
    
    if result.returncode != 0:
        print("Installing packages (this may take a moment)...", file=sys.stderr)
        subprocess.run(
            [str(VENV_PYTHON), "-m", "pip", "install", "--quiet"] + PACKAGES,
            check=True
        )
        print("Packages installed successfully.", file=sys.stderr)


def convert_pdf(pdf_path: Path, include_headers: bool = True, include_footers: bool = True) -> Path:
    """Convert PDF to markdown using the venv's Python with enhanced layout analysis."""
    output_path = pdf_path.with_suffix(".md")
    
    # Run conversion in the venv
    # Import pymupdf.layout FIRST to activate enhanced layout analysis
    conversion_script = f"""
import pymupdf.layout  # Must import first to enable enhanced layout analysis
import pymupdf4llm
import pathlib

pdf_path = pathlib.Path({repr(str(pdf_path))})
output_path = pathlib.Path({repr(str(output_path))})

md_text = pymupdf4llm.to_markdown(
    str(pdf_path),
    header={include_headers},
    footer={include_footers}
)
output_path.write_text(md_text, encoding='utf-8')
print(f"Converted: {{output_path}}")
"""
    
    result = subprocess.run(
        [str(VENV_PYTHON), "-c", conversion_script],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"Error converting PDF: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    
    print(result.stdout, end="")
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Convert PDF to markdown with enhanced layout analysis"
    )
    parser.add_argument("pdf_path", help="Path to the PDF file")
    parser.add_argument(
        "--no-headers",
        action="store_true",
        help="Exclude page headers from output"
    )
    parser.add_argument(
        "--no-footers",
        action="store_true",
        help="Exclude page footers from output"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-convert even if markdown already exists"
    )
    
    args = parser.parse_args()
    
    pdf_path = Path(args.pdf_path).resolve()
    
    if not pdf_path.exists():
        print(f"Error: File not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)
    
    if not pdf_path.suffix.lower() == ".pdf":
        print(f"Error: Not a PDF file: {pdf_path}", file=sys.stderr)
        sys.exit(1)
    
    # Check if already converted
    md_path = pdf_path.with_suffix(".md")
    if md_path.exists() and not args.force:
        print(f"Already converted: {md_path}")
        return
    
    # Setup environment and convert
    ensure_venv()
    ensure_packages()
    convert_pdf(
        pdf_path,
        include_headers=not args.no_headers,
        include_footers=not args.no_footers
    )


if __name__ == "__main__":
    main()
