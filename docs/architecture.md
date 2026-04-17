# Architecture

This repository packages one workflow into one portable GitHub project:

1. NotebookLM gathers and synthesizes source material.
2. Raw artifacts are downloaded with provenance.
3. Parsers extract the most important claims.
4. LLM Wiki pages are updated with comparisons, checklists, entities, and summaries.
5. Obsidian acts as the human-readable editing surface.
6. qmd indexes the resulting notes for retrieval.

The crucial design principle is that the wiki should store the high-signal claims, obligations, constraints, numbers, and governance details — not just generic summaries.
