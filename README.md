# Paper Agent

A demonstration project for [Remind](https://github.com/sandst1/remind) **v0.12.3** — an agent-driven memory layer for LLMs. An AI agent reads scientific papers, stores what it learns in Remind, and curates that knowledge into durable concepts that persist across sessions.

The goal is not just to collect PDFs. It is to build a **growing, queryable knowledge base** about the papers you read: findings, methods, connections between ideas, open questions, and contradictions — all structured so future sessions can recall and build on prior work.

![Paper Agent: AI-Powered Research Paper Processing](paperagent.png)

## Prerequisites

- **[Remind 0.12.3](https://github.com/sandst1/remind)** — install with a pinned version:

  ```bash
  pip install remind-mcp==0.12.3
  ```

  Remind uses local embeddings by default (no API key required). See the [Remind docs](https://sandst1.github.io/remind/) for configuration options.

- **Python 3.11+** — for the helper scripts and PDF conversion
- **Cursor** (or another agent-capable IDE) — the workflow is designed for an AI agent that follows [`AGENTS.md`](AGENTS.md)

This repository demonstrates Remind's current capture → consolidate → recall cycle on a real, multi-paper reading task (mostly LLM architecture papers).

## How it works

The system keeps two complementary stores:

| Store | What it holds | Where |
|-------|---------------|-------|
| **Files on disk** | PDFs, converted markdown caches, a human-readable index | `papers/` |
| **Remind memory** | Episodes (raw insights), concepts (generalized knowledge), entity graph | `.remind/remind.db` |

Files tell you *which papers exist*. Remind tells you *what you learned from them* and how ideas connect.

### End-to-end: from URL to curated memory

Here is the full journey, in plain terms.

```
  arXiv URL or PDF
        │
        ▼
  papers/incoming/          ← download or drop the file
        │
        ▼
  Agent reads the paper     ← PDF → markdown, then comprehension
        │
        ▼
  Remind episodes           ← raw observations tagged with entities
        │
        ▼
  Remind concepts           ← consolidated, durable knowledge
        │
        ▼
  papers/library/ + INDEX   ← paper archived, index updated
```

**1. Acquire the paper**

Give the agent an arXiv URL, a direct PDF link, or drop a PDF into `papers/incoming/`. The download skill fetches the paper and names the file `{arxiv-id}-{title-slug}.pdf`.

**2. Queue and pick up**

`papers/incoming/` is the inbox — papers waiting to be read. The agent picks the oldest unprocessed paper (or one you name) and checks Remind first to see if anything is already known about it.

**3. Read**

The PDF is converted to markdown (cached alongside the PDF so it only runs once). The agent reads the full text and extracts what matters: contributions, methods, definitions, limitations, and links to other work.

**4. Capture episodes**

Each insight is stored in Remind as an **episode** — a raw observation tagged with entities like `paper:attention-is-all-you-need` and `concept:transformers`, plus an optional topic (e.g. `ml-architecture`). Remind surfaces nearby existing memories on every write, so contradictions are caught early.

**5. Build connections**

The agent queries related topics already in memory and records cross-paper relationships: how a new method relates to prior work, which paper introduced which concept, and so on. Entity relations (`introduced`, `extends`, etc.) form a knowledge graph.

**6. Curate into concepts**

Raw episodes are not enough. The agent **consolidates** related episodes into **concepts** — generalized insights that apply beyond a single paper — and links evidence back to the source episodes. Conflicts are resolved or dismissed. A paper is not considered fully processed until Remind reports a clean health check (no pending episodes, no orphan concepts).

This is the core Remind pattern: the agent is the intelligence; Remind is the deterministic substrate that stores, retrieves, and tracks memory quality.

**7. Archive and index**

Once memory is curated, the PDF and its markdown cache move from `incoming/` to `library/`, and an entry is added to `papers/INDEX.md` linking the file on disk to the Remind entity. Future sessions can cross-reference both.

### What you can ask afterward

Because knowledge lives in Remind, not just in chat history:

- *"What do we know about mixture-of-experts?"* — semantic recall across all processed papers
- *"Compare scaling laws across papers"* — agent recalls related concepts and synthesizes
- *"What open questions remain about RLHF?"* — query question-type episodes

## Project layout

```
papers/
  incoming/     Papers waiting to be processed
  library/      Fully read papers (PDF + .md cache)
  INDEX.md      Human-readable record of every processed paper
scripts/
  inbox.py      Inbox pipeline: list, next, done
  index.py      Maintain INDEX.md
.claude/skills/
  download-paper/   Fetch papers from arXiv or URLs
  read-pdf/         Convert PDFs to agent-readable markdown
  remind-capture/   When and how to write memories
  remind-context/   When and how to recall before acting
  remind-curate/    Consolidate episodes into concepts
.remind/
  remind.db     Remind memory database (local to this project)
AGENTS.md       Full agent workflow instructions
```

## Getting started

Install Remind, clone this repo, and open it in Cursor.

**Download a paper:**

```bash
python .claude/skills/download-paper/scripts/download_arxiv.py \
  "https://arxiv.org/abs/2501.12948" \
  --output-dir papers/incoming/
```

**Ask the agent to process it:**

> Process the next paper in incoming.

Or name a specific file:

> Process `2412-15115-qwen25-technical-report.pdf`.

**Check status yourself:**

```bash
python scripts/inbox.py list          # what's waiting
python scripts/inbox.py next          # oldest unprocessed paper
python scripts/index.py list          # what's already in the library
remind recall "recent papers" -k 5    # what's in memory
remind snapshot health                # memory quality check
```

## For agents

See [`AGENTS.md`](AGENTS.md) for the complete step-by-step workflow, entity naming conventions, and Remind CLI reference. That file is the operational spec the agent follows when processing papers.

## About Remind

[Remind](https://github.com/sandst1/remind) is a memory layer where **the agent is the only intelligence**. It provides:

- **Episodes** — raw experiences (observations, decisions, facts, questions)
- **Concepts** — generalized knowledge distilled from episodes
- **Semantic recall** — find relevant memories by meaning, entity, or topic
- **Collision detection** — surface contradictions when new facts arrive
- **Evidence-weighted retrieval** — concepts backed by more evidence rank higher
- **Transactional curation** — batch consolidate, resolve conflicts, link entities atomically

This project is a practical demonstration of that model applied to scientific paper reading — turning a stream of PDFs into a curated, persistent knowledge base.
