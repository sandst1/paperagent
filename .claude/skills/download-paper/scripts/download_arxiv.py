#!/usr/bin/env python3
"""
Download a paper from arXiv or a direct PDF URL.
Automatically manages virtual environment and dependencies.
"""

import subprocess
import sys
import os
import re
import argparse
from pathlib import Path
from urllib.parse import urlparse, unquote

# Paths
SCRIPT_DIR = Path(__file__).parent.resolve()
SKILL_DIR = SCRIPT_DIR.parent
VENV_DIR = SKILL_DIR / ".venv"
VENV_PYTHON = VENV_DIR / "bin" / "python"

# Find workspace root (go up until we find .cursor or hit filesystem root)
def find_workspace_root():
    current = SCRIPT_DIR
    while current != current.parent:
        if (current / ".cursor").exists():
            return current
        current = current.parent
    return SCRIPT_DIR.parent.parent.parent.parent  # Fallback


def ensure_venv():
    """Create virtual environment if it doesn't exist."""
    if not VENV_DIR.exists():
        print(f"Creating virtual environment at {VENV_DIR}...", file=sys.stderr)
        subprocess.run([sys.executable, "-m", "venv", str(VENV_DIR)], check=True)
        print("Virtual environment created.", file=sys.stderr)


def ensure_packages():
    """Install required packages if not already installed."""
    required = ["requests", "beautifulsoup4"]
    
    for package in required:
        import_name = "bs4" if package == "beautifulsoup4" else package
        result = subprocess.run(
            [str(VENV_PYTHON), "-c", f"import {import_name}"],
            capture_output=True
        )
        
        if result.returncode != 0:
            print(f"Installing {package}...", file=sys.stderr)
            subprocess.run(
                [str(VENV_PYTHON), "-m", "pip", "install", "--quiet", package],
                check=True
            )
            print(f"{package} installed.", file=sys.stderr)


def is_arxiv_url(url: str) -> bool:
    """Check if the URL is an arXiv URL."""
    return "arxiv.org" in url.lower()


def is_direct_pdf_url(url: str) -> bool:
    """Check if the URL appears to be a direct PDF link."""
    parsed = urlparse(url.lower())
    path = parsed.path
    # Check if path ends with .pdf
    if path.endswith(".pdf"):
        return True
    # Could also be a PDF without extension (we'll verify via content-type during download)
    return False


def extract_arxiv_id(url: str) -> str:
    """Extract the arXiv ID from various URL formats."""
    # Match patterns like:
    # https://arxiv.org/abs/2502.04463
    # https://arxiv.org/pdf/2502.04463
    # https://arxiv.org/pdf/2502.04463.pdf
    # arxiv.org/abs/2502.04463
    patterns = [
        r"arxiv\.org/(?:abs|pdf)/(\d+\.\d+)",
        r"arxiv\.org/(?:abs|pdf)/([a-z-]+/\d+)",  # Old format like hep-th/9901001
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url, re.IGNORECASE)
        if match:
            return match.group(1)
    
    raise ValueError(f"Could not extract arXiv ID from URL: {url}")


def extract_filename_from_url(url: str) -> str:
    """Extract a filename from a URL."""
    parsed = urlparse(url)
    path = unquote(parsed.path)
    filename = Path(path).name
    
    # If no filename or doesn't look like a PDF name, generate one
    if not filename or filename == "/" or len(filename) < 3:
        # Use domain + path hash as fallback
        import hashlib
        hash_part = hashlib.md5(url.encode()).hexdigest()[:8]
        filename = f"paper-{hash_part}.pdf"
    
    # Ensure .pdf extension
    if not filename.lower().endswith(".pdf"):
        filename = filename + ".pdf"
    
    return filename


def slugify(text: str, max_length: int = 60) -> str:
    """Convert text to a URL-friendly slug."""
    # Lowercase
    text = text.lower()
    # Replace spaces and underscores with hyphens
    text = re.sub(r"[\s_]+", "-", text)
    # Remove non-alphanumeric characters except hyphens
    text = re.sub(r"[^a-z0-9-]", "", text)
    # Collapse multiple hyphens
    text = re.sub(r"-+", "-", text)
    # Trim hyphens from ends
    text = text.strip("-")
    # Truncate
    if len(text) > max_length:
        text = text[:max_length].rsplit("-", 1)[0]
    return text


def download_arxiv_paper(arxiv_id: str, output_dir: Path) -> Path:
    """Download an arXiv paper using the venv's Python."""
    download_script = f'''
import requests
from bs4 import BeautifulSoup
import re
from pathlib import Path

arxiv_id = {repr(arxiv_id)}
output_dir = Path({repr(str(output_dir))})

def slugify(text, max_length=60):
    text = text.lower()
    text = re.sub(r"[\\s_]+", "-", text)
    text = re.sub(r"[^a-z0-9-]", "", text)
    text = re.sub(r"-+", "-", text)
    text = text.strip("-")
    if len(text) > max_length:
        text = text[:max_length].rsplit("-", 1)[0]
    return text

# Fetch paper metadata
abs_url = f"https://arxiv.org/abs/{{arxiv_id}}"
print(f"Fetching metadata from {{abs_url}}...")
response = requests.get(abs_url, timeout=30)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")
title_elem = soup.find("h1", class_="title")
if title_elem:
    # Remove "Title:" prefix if present
    title = title_elem.get_text().replace("Title:", "").strip()
else:
    title = arxiv_id

# Create filename
slug = slugify(title)
# Replace dots in arxiv_id for filename (2502.04463 -> 2502-04463)
safe_id = arxiv_id.replace("/", "-").replace(".", "-")
filename = f"{{safe_id}}-{{slug}}.pdf"
output_path = output_dir / filename

# Check if already exists
if output_path.exists():
    print(f"Already exists: {{output_path}}")
else:
    # Download PDF
    pdf_url = f"https://arxiv.org/pdf/{{arxiv_id}}.pdf"
    print(f"Downloading from {{pdf_url}}...")
    pdf_response = requests.get(pdf_url, timeout=60)
    pdf_response.raise_for_status()
    
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(pdf_response.content)
    print(f"Saved: {{output_path}}")

print(f"RESULT:{{output_path}}")
'''
    
    result = subprocess.run(
        [str(VENV_PYTHON), "-c", download_script],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"Error downloading paper: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    
    # Print output
    for line in result.stdout.strip().split("\n"):
        if line.startswith("RESULT:"):
            output_path = Path(line.replace("RESULT:", ""))
        else:
            print(line)
    
    return output_path


def download_direct_pdf(url: str, output_dir: Path, custom_name: str = None) -> Path:
    """Download a PDF from a direct URL using the venv's Python."""
    default_filename = custom_name if custom_name else extract_filename_from_url(url)
    
    download_script = f'''
import requests
from pathlib import Path
import re

url = {repr(url)}
output_dir = Path({repr(str(output_dir))})
default_filename = {repr(default_filename)}

def slugify(text, max_length=60):
    text = text.lower()
    text = re.sub(r"[\\s_]+", "-", text)
    text = re.sub(r"[^a-z0-9-]", "", text)
    text = re.sub(r"-+", "-", text)
    text = text.strip("-")
    if len(text) > max_length:
        text = text[:max_length].rsplit("-", 1)[0]
    return text

print(f"Downloading PDF from {{url}}...")

# Make request with headers to avoid being blocked
headers = {{
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}}
response = requests.get(url, timeout=60, headers=headers, allow_redirects=True)
response.raise_for_status()

# Verify it's actually a PDF
content_type = response.headers.get("Content-Type", "").lower()
if "pdf" not in content_type and not response.content[:4] == b"%PDF":
    raise ValueError(f"URL does not appear to be a PDF (Content-Type: {{content_type}})")

# Try to get filename from Content-Disposition header
filename = default_filename
content_disp = response.headers.get("Content-Disposition", "")
if "filename=" in content_disp:
    import re
    # Extract filename from Content-Disposition header
    for part in content_disp.split(";"):
        part = part.strip()
        if part.startswith("filename="):
            filename = part[9:].strip().strip('"').strip("'")
            if not filename.lower().endswith(".pdf"):
                filename = filename + ".pdf"
            break

# Sanitize filename
filename = re.sub(r'[<>:"/\\\\|?*]', "-", filename)
output_path = output_dir / filename

# Check if already exists
if output_path.exists():
    print(f"Already exists: {{output_path}}")
else:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(response.content)
    print(f"Saved: {{output_path}}")

print(f"RESULT:{{output_path}}")
'''
    
    result = subprocess.run(
        [str(VENV_PYTHON), "-c", download_script],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"Error downloading PDF: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    
    # Print output
    output_path = None
    for line in result.stdout.strip().split("\n"):
        if line.startswith("RESULT:"):
            output_path = Path(line.replace("RESULT:", ""))
        else:
            print(line)
    
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Download a paper from arXiv or a direct PDF URL")
    parser.add_argument("url", help="arXiv URL or direct PDF URL")
    parser.add_argument("--output-dir", "-o", help="Output directory (default: papers/)")
    parser.add_argument("--name", "-n", help="Custom filename for direct PDF downloads (without .pdf extension)")
    args = parser.parse_args()
    
    # Determine output directory
    if args.output_dir:
        output_dir = Path(args.output_dir).resolve()
    else:
        output_dir = find_workspace_root() / "papers"
    
    # Setup environment
    ensure_venv()
    ensure_packages()
    
    # Determine URL type and download accordingly
    if is_arxiv_url(args.url):
        # Extract arXiv ID and download
        try:
            arxiv_id = extract_arxiv_id(args.url)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        
        print(f"Detected arXiv URL")
        print(f"arXiv ID: {arxiv_id}")
        output_path = download_arxiv_paper(arxiv_id, output_dir)
    else:
        # Treat as direct PDF URL
        print(f"Detected direct PDF URL")
        custom_name = f"{args.name}.pdf" if args.name else None
        output_path = download_direct_pdf(args.url, output_dir, custom_name)
    
    print(f"\nPaper downloaded successfully!")
    print(f"Path: {output_path}")


if __name__ == "__main__":
    main()
