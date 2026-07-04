---
name: read-pdf
description: Read PDF files by converting them to markdown. Use when the agent needs to read, analyze, or extract content from a PDF file. Handles caching (converts once, reads from cache thereafter) and automatically manages the Python virtual environment and dependencies.
---

# Read PDF

Convert PDF files to markdown for reading using enhanced layout analysis. Cached conversions are stored alongside the original PDF.

**Features:**
- Enhanced layout analysis (via `pymupdf-layout`) for better text extraction
- Automatic OCR when beneficial (if Tesseract installed)
- Option to exclude repetitive headers/footers
- Caches conversions for faster re-reads

## Workflow

1. **Check for cached markdown**: Look for `<filename>.md` in the same directory as the PDF
2. **If cached**: Read and use the markdown file directly
3. **If not cached**: Run the conversion script, then read the resulting markdown

## Step-by-step

### Step 1: Check for existing markdown

For a PDF at `path/to/document.pdf`, check if `path/to/document.md` exists.

```bash
# Example: checking for papers/example.pdf
ls papers/example.md
```

If the `.md` file exists, read it directly with the Read tool and skip to Step 3.

### Step 2: Convert the PDF (if no cache)

Run the conversion script:

```bash
python .claude/skills/read-pdf/scripts/convert_pdf.py "path/to/document.pdf"
```

**Options:**
- `--no-headers` — Exclude page headers (useful for repetitive titles/logos)
- `--no-footers` — Exclude page footers (useful for repetitive page numbers)
- `--force` — Re-convert even if markdown cache exists

The script will:
- Create `.claude/skills/read-pdf/.venv` if it doesn't exist
- Install `pymupdf4llm` and `pymupdf-layout` in the venv
- Convert the PDF to markdown with enhanced layout analysis
- Save `document.md` alongside `document.pdf`

**Note**: First run may take 30-60 seconds to set up the environment.

### Step 3: Read the markdown

Use the Read tool to read the generated markdown file:
- Input: `path/to/document.pdf`
- Output: `path/to/document.md`

## Examples

**Example 1: Reading a paper**
```
User: "Read the paper at papers/attention.pdf"

1. Check: ls papers/attention.md → not found
2. Convert: python .claude/skills/read-pdf/scripts/convert_pdf.py "papers/attention.pdf"
3. Read: papers/attention.md
```

**Example 2: Cached read**
```
User: "What does papers/attention.pdf say about transformers?"

1. Check: ls papers/attention.md → exists!
2. Read: papers/attention.md (skip conversion)
```

**Example 3: Clean extraction without headers/footers**
```
User: "Read this paper but skip the repetitive headers"

1. Check: ls papers/example.md → exists (but need cleaner version)
2. Convert: python .claude/skills/read-pdf/scripts/convert_pdf.py "papers/example.pdf" --no-headers --no-footers --force
3. Read: papers/example.md
```

## Troubleshooting

If conversion fails:
- Ensure the PDF path is correct and the file exists
- Check that Python 3 is available: `python3 --version`
- For corrupted PDFs, the script will output an error message
- If layout analysis fails, try re-running (transient issues can occur)
