---
name: download-paper
description: Download research papers from arXiv or direct PDF URLs. Use when the user provides an arXiv link, a direct PDF URL, or asks to fetch/get/save/download a paper.
---

# Download Paper

Download research papers from arXiv or direct PDF URLs and save them to the papers folder.

## Supported Sources

- **arXiv**: URLs like `https://arxiv.org/abs/2502.04463`
- **Direct PDF**: Any URL ending in `.pdf` or serving PDF content

## Usage

Run the download script with a URL:

```bash
python .claude/skills/download-paper/scripts/download_arxiv.py "<url>"
```

### arXiv Papers

The script auto-detects arXiv URLs and will:
1. Extract the paper ID from the URL
2. Fetch the paper title from arXiv
3. Download the PDF
4. Save to `papers/` as `{id}-{title-slug}.pdf`

**Example**:
```bash
python .claude/skills/download-paper/scripts/download_arxiv.py "https://arxiv.org/abs/2502.04463"
# Output: papers/2502-04463-training-language-models-to-reason-efficiently.pdf
```

### Direct PDF URLs

For non-arXiv URLs, the script treats them as direct PDF links:
1. Downloads the PDF from the URL
2. Uses the filename from the URL or Content-Disposition header
3. Verifies the content is actually a PDF

**Example**:
```bash
python .claude/skills/download-paper/scripts/download_arxiv.py "https://example.com/research/paper.pdf"
# Output: papers/paper.pdf
```

## Options

```bash
# Download to default location (papers/)
python .claude/skills/download-paper/scripts/download_arxiv.py "<url>"

# Download to specific directory
python .claude/skills/download-paper/scripts/download_arxiv.py "<url>" --output-dir papers/ml

# Specify custom filename for direct PDF downloads
python .claude/skills/download-paper/scripts/download_arxiv.py "<url>" --name "my-paper-name"
# Output: papers/my-paper-name.pdf
```

## After Downloading

After downloading a paper, you can:
1. Use the **read-pdf** skill to read its contents
2. Use **Remind** tools to store interesting knowledge

## Troubleshooting

- **"URL does not appear to be a PDF"**: The URL didn't return PDF content. Check the URL is correct.
- **"Invalid arXiv URL"**: For arXiv links, ensure URL format is `https://arxiv.org/abs/{id}` or `https://arxiv.org/pdf/{id}`
- **Network errors**: Check internet connection; some sites may block automated downloads
- **First run slow**: Initial setup creates a virtual environment and installs dependencies
