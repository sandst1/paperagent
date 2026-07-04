# Papers - Agent Instructions

This project is for reading and organizing scientific papers.

## Folder Layout

```
papers/
  incoming/   ← papers waiting to be processed (unread)
  library/    ← papers fully read and memorized (PDF + .md cache)
  INDEX.md    ← human-readable record of every processed paper
scripts/
  inbox.py    ← incoming→library pipeline (list / next / done)
  index.py    ← add entries to INDEX.md and list them
```

Drop a PDF into `papers/incoming/` (manually or via download) and ask to process it.

## Core Capabilities

1. **download-paper skill** — Downloads papers from arXiv or direct PDF URLs
2. **read-pdf skill** — Converts PDFs to agent-readable markdown (cached alongside PDF)
3. **remind skills** — Persistent external memory across sessions (context, capture, curate)
4. **inbox.py** — File-level pipeline management (list, next, done)
5. **index.py** — Maintains `papers/INDEX.md`, the permanent record of processed papers

---

## Inbox Commands

```bash
python scripts/inbox.py list          # Show all papers waiting in incoming/
python scripts/inbox.py next          # Print path to the oldest unprocessed paper
python scripts/inbox.py done <path>   # Move paper + .md cache to library/ after processing
```

## Index Commands

```bash
python scripts/index.py list          # Print papers/INDEX.md

python scripts/index.py add <pdf> \
  --title  "Full Paper Title" \
  --entity "paper:short-name" \       # Remind entity used to tag memories
  --url    "https://arxiv.org/..." \  # Source URL (optional but recommended)
  --topic  "ml-architecture" \        # Remind topic tag (optional)
  --notes  "one-liner summary"        # Optional short note
```

`index.py add` auto-derives the entity slug from the title if `--entity` is omitted.

---

## Session Start

Always orient yourself before acting:

```bash
remind recall "recent papers read" -k 5
remind snapshot stats pending
python scripts/inbox.py list          # papers waiting to be processed
python scripts/index.py list          # papers already in the library
```

---

## Workflow: "Download N papers into incoming"

Use the download-paper skill with `--output-dir papers/incoming/`:

```bash
python .cursor/skills/download-paper/scripts/download_arxiv.py "<url>" --output-dir papers/incoming/
```

Repeat for each URL. Then `python scripts/inbox.py list` to confirm.

---

## Workflow: "Process next paper" / "Process paper X"

This is the core loop. Run it for one paper at a time.

### 1. Identify the paper

```bash
# Next in queue:
python scripts/inbox.py next
# → papers/incoming/2502-04463-some-title.pdf

# Or a specific paper named by the user — locate it in incoming/
```

### 2. Check existing knowledge

```bash
remind recall "paper:<short-name>"
remind recall "<paper title or key topic>"
```

- Substantial knowledge exists → summarize, ask if user wants a re-read
- Partial knowledge → note what you know, then proceed to fill gaps
- No knowledge → proceed

### 3. Convert and read

```bash
# Check for cached markdown first
ls papers/incoming/<filename>.md   # if exists, skip conversion

# Convert if needed
python .cursor/skills/read-pdf/scripts/convert_pdf.py "papers/incoming/<filename>.pdf"

# Read the markdown with the Read tool
```

### 4. Store key insights (mandatory)

After reading, capture insights with `remind remember`. This is not optional.

```bash
remind remember "content of insight" \
  -t observation \
  -e concept:transformers,paper:attention-is-all-you-need \
  --topic ml-architecture
```

**What to capture:**
- Key findings and contributions
- Novel methods or techniques  
- Important definitions and concepts
- Connections to other papers / ideas
- Limitations acknowledged by authors
- Open questions raised (`-t question`)

**What to skip:** boilerplate, author lists, obvious statements, things already in memory.

**Always check `remember` output.** It shows nearby similar episodes and collision warnings:
- Nearby item contradicts what you stored → issue a `conflict` op
- New fact supersedes an older one → `supersede old=<id> new=<id> note="reason"`
- Complementary or unrelated → continue

### 5. Build connections

Query memory for related topics, then capture relationship insights:

```bash
remind recall "attention mechanisms" -k 8
remind remember "Self-attention in Transformers generalizes seq2seq attention by attending to the same sequence" \
  -t observation -e concept:self-attention,concept:attention
```

Capture entity relationships when meaningful:

```bash
remind apply << 'EOF'
remember as=r1 t=observation e=paper:attention-is-all-you-need,concept:transformers "Introduced the Transformer architecture"
entity_relation source=paper:attention-is-all-you-need target=concept:transformers relation=introduced strength=1.0
EOF
```

### 6. Curate memory (mandatory — do not skip)

Raw episodes are not enough. After storing insights, you MUST consolidate them into durable concepts before moving on. A paper is not fully processed until `remind snapshot health` reports 0 pending episodes and 0 orphan concepts.

Consolidate the episodes from this paper into concepts:

```bash
remind snapshot pending conflicts health
```

For each major theme in the pending episodes, group related ones into a concept. Also add evidence links so Recall can rank concepts by support:

```bash
remind apply << 'EOF'
concept as=c1 from=ep:11,ep:12 title="Pattern name" "Generalized insight that applies beyond these episodes."
link from=$c1 to=concept:related-concept type=specializes
evidence concept=$c1 episode=ep:11 type=supports strength=1.0 "why ep:11 supports this"
evidence concept=$c1 episode=ep:12 type=supports strength=1.0 "why ep:12 supports this"
entity_relation source=paper:short-name target=concept:key-idea relation=introduced strength=1.0
EOF
```

Then mark source episodes as consolidated directly (the `processed` CLI op does not persist reliably):

```bash
sqlite3 .remind/remind.db "UPDATE episodes SET consolidated=1 WHERE id IN ('ep1id','ep2id');"
```

Resolve any conflicts:
- `resolve id=conflict:7 winner=fact:b3d01 "reason"` — one claim is correct
- `dismiss id=conflict:7 "both true: different contexts"` — both claims valid in context

Verify health is clean before moving on:

```bash
remind snapshot health
# → Healthy: True, 0 pending, 0 orphans
```

### 7. Move to library and record in index

Only proceed here once `remind snapshot health` shows **Healthy: True**. Then do both steps:

```bash
# Move files
python scripts/inbox.py done "papers/incoming/<filename>.pdf"
# → moves <filename>.pdf and <filename>.md to papers/library/

# Record in index (use the same entity name you tagged memories with)
python scripts/index.py add "papers/incoming/<filename>.pdf" \
  --title  "Full Paper Title" \
  --entity "paper:short-name" \
  --url    "https://arxiv.org/abs/..." \
  --topic  "ml-architecture" \
  --notes  "one-line summary of key contribution"
```

The index entry links the file on disk to the Remind entity so future sessions can cross-reference both.

---

---

## Common Tasks

### "Check incoming" / "What's in the queue?"
```bash
python scripts/inbox.py list
```

### "What papers have we processed?" / "Show the library"
```bash
python scripts/index.py list
```

### "Download paper X"
```bash
python .cursor/skills/download-paper/scripts/download_arxiv.py "<url>" --output-dir papers/incoming/
```

### "Process next paper"
Follow the 6-step workflow above starting with `python scripts/inbox.py next`.

### "Process paper X" (specific paper already in incoming)
Follow the 6-step workflow with the named file.

### "What do you know about X?"
```bash
remind recall "X" -k 8
```
Synthesize and present findings; note gaps.

### "Compare papers on topic Y"
```bash
remind recall "topic Y" -k 10
```
Read any new papers, store comparison insights with shared entities.

### "Find papers related to Z"
```bash
remind recall "Z"
remind snapshot entities:paper    # list all known paper entities
ls papers/incoming/ papers/library/  # check for unprocessed PDFs
```

---

## Entity Naming for Papers

| Type | Use for | Example |
|------|---------|---------|
| `paper:<short-name>` | Papers | `paper:attention-is-all-you-need`, `paper:bert` |
| `concept:<name>` | Abstract ideas, techniques | `concept:transformers`, `concept:attention` |
| `person:<name>` | Researchers | `person:hinton`, `person:vaswani` |
| `tool:<name>` | Frameworks, tools | `tool:pytorch`, `tool:jax` |

---

## Remind CLI Quick Reference

```bash
# Recall
remind recall "query"                              # Semantic search
remind recall "query" --entity paper:bert          # Everything about a specific entity
remind recall "query" --topic ml-architecture      # Topic-scoped
remind recall "query" -k 10                        # More results
remind snapshot entities:paper                     # All known paper entities
remind snapshot questions                          # Open question episodes
remind snapshot pending conflicts health           # Session overview

# Capture
remind remember "content" -t <type> -e <entities> --topic <topic>
# Types: observation, decision, outcome, preference, fact, question

# Batch apply
remind apply << 'EOF'
remember as=r1 t=observation e=concept:x "..."
concept as=c1 from=ep:11,ep:12 title="..." "..."
entity_relation source=paper:x target=concept:y relation=introduced strength=1.0
processed ids=ep:11,ep:12
EOF

# Conflicts
remind conflicts list
remind apply 'resolve id=conflict:7 winner=fact:b3d01 "reason"'
remind apply 'dismiss id=conflict:7 "both contexts valid"'
```
