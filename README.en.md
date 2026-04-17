# notebooklm-llm-wiki-flow

[![CI](https://github.com/reallygood83/notebooklm-llm-wiki-flow/actions/workflows/ci.yml/badge.svg)](https://github.com/reallygood83/notebooklm-llm-wiki-flow/actions)

English documentation.
한국어 문서는 여기: [README.md](./README.md)

===

Overview

notebooklm-llm-wiki-flow is a local-first Python CLI that turns NotebookLM output into reusable knowledge assets through:

NotebookLM → LLM Wiki → Obsidian → qmd

The key idea is that NotebookLM is not the final destination.
NotebookLM gathers and synthesizes source material, but the real long-term knowledge layer is the LLM Wiki.

===

What this project does

1. Feed URLs or PDFs into NotebookLM.
2. Generate report, mind map, and Q&A artifacts.
3. Extract only the high-signal, decision-relevant content.
4. Save it into an LLM Wiki structure inside Obsidian.
5. Re-index it with qmd for later retrieval.

===

What is the LLM Wiki?

The LLM Wiki is not a dump of every LLM response.
It is a structured knowledge layer that stores only information worth keeping for future decisions and reuse.

Main page types
- Raw source
  - original text plus provenance
- Entity
  - accumulated knowledge about an organization, product, or concept
- Comparison
  - side-by-side analysis
- Query / Checklist
  - reusable operational checklist

===

Practical user benefits

1. Safer outputs
- staged writes reduce half-written file states
- manifest.json makes each run auditable

2. More trustworthy automation
- NotebookLM CLI failures are wrapped with typed errors and step context
- fake-client integration tests validate the core flow without real NotebookLM sessions

3. Less confusing setup
- clear precedence:
  - environment variables > project.yaml > .env > defaults
- bootstrap fails loudly instead of hiding install problems

4. More stable note quality
- deterministic index rebuild
- template-based entity rendering
- parser fallback for non-table reports

5. Easier collaboration and shipping
- ruff
- mypy
- pytest
- coverage gate
- GitHub Actions on Ubuntu + macOS

===

Core features

- `nlwflow` CLI
- NotebookLM client protocol
- typed flow phases
- staged writes + manifest
- deterministic wiki index update
- fake-client integration coverage
- Jinja2 entity templates
- parser fallback for non-table reports
- qmd integration
- GitHub Actions CI

===

Prerequisites

- Python 3.11+
- Node.js 20+ and npm (for the qmd indexer; skip with `INSTALL_QMD_GLOBAL=0`)
- pipx (optional — only needed for the isolated `USE_PIPX=1` path)

===

Install paths — two options

`notebooklm-py` now installs automatically through the `[notebooklm]` extra.

**A. One-shot install (recommended) — `./scripts/bootstrap.sh`**

This does everything for you:

1. Creates `.venv` and editable-installs this project
2. `pip install -e ".[dev,notebooklm]"` — nlwflow + **notebooklm-py** + Playwright all inside the venv
3. `python -m playwright install chromium`
4. `npm install -g @tobilu/qmd` (optional)

**B. Install directly with pip**

```bash
python3.11 -m venv .venv
./.venv/bin/pip install -e ".[notebooklm]"
./.venv/bin/python -m playwright install chromium
# qmd separately: npm install -g @tobilu/qmd
```

**C. Prefer isolation (legacy)**

```bash
USE_PIPX=1 ./scripts/bootstrap.sh
```

With this path, `notebooklm-py` is installed into a separate pipx environment
at `~/.local/pipx/venvs/notebooklm-py/`, outside this project's venv.

===

Quick start

1. Clone the repository
2. Run `./scripts/bootstrap.sh`
3. Run `notebooklm login` — one-time browser login
4. Run `./.venv/bin/nlwflow init-config`
5. Run `./.venv/bin/nlwflow doctor --json`
6. Optionally install the starter kit
   - `./.venv/bin/nlwflow install-obsidian-kit --vault /path/to/vault`
7. Run the built-in workflow
   - `./.venv/bin/nlwflow run-policy-compare --json`
8. Run a reusable YAML workflow
   - `./.venv/bin/nlwflow run-from-yaml examples/policy-compare-anthropic-openai-education.yaml --json`

===

CLI commands

- `nlwflow --version`
  - print version
- `nlwflow doctor`
  - check environment and paths
- `nlwflow init-config`
  - create a starter config
- `nlwflow plan-policy-compare`
  - print the built-in source pack
- `nlwflow run-policy-compare`
  - run NotebookLM and update wiki/obsidian/qmd
- `nlwflow run-from-yaml WORKFLOW.yaml`
  - run a reusable YAML workflow
- `nlwflow install-claude-skill`
  - install the `/note-wiki` slash command into Claude Code (`~/.claude/commands/note-wiki.md`)
- `nlwflow install-obsidian-kit`
  - install a starter vault layout
- `nlwflow score-report REPORT.md`
  - extract high-signal sections

===

Claude Code `/note-wiki` slash command

Installing this project also ships a `/note-wiki` slash command for Claude Code.
Give it a prompt and one or more source URLs, and Claude will drive the
`nlwflow note-wiki` CLI to run the full NotebookLM → LLM Wiki → Obsidian pipeline
for you.

Install

```bash
./.venv/bin/nlwflow install-claude-skill
# → writes ~/.claude/commands/note-wiki.md
# If you cloned this repo, .claude/commands/note-wiki.md is already available
# as a project-level slash command.
```

Example usage inside Claude Code

```
/note-wiki Compare Anthropic and OpenAI education policies
  https://www.anthropic.com/legal/aup
  https://openai.com/policies/usage-policies/
```

Claude will automatically:
1. Run `nlwflow note-wiki "..." --dry-run --json` to preview the plan
2. Ask for confirmation, then execute the real run
3. Summarize the result (notebook_id, comparison_page, manifest_path)

Use `--target` to change the install location or `--force` to overwrite.

===

Configuration precedence

1. `NLWFLOW_*` environment variables
2. `project.yaml`
3. `.env`
4. defaults

Common environment variables
- `NLWFLOW_OBSIDIAN_VAULT`
- `NLWFLOW_WIKI_PATH`
- `NLWFLOW_NOTEBOOKLM_COMMAND`
- `NLWFLOW_QMD_COMMAND`
- `NLWFLOW_QMD_COLLECTION`

===

Repository layout

- `src/notebooklm_llm_wiki_flow/`
  - Python package and CLI
- `config/`
  - config and prompts
- `examples/`
  - reusable workflow examples
- `templates/`
  - markdown / Jinja templates
- `docs/`
  - architecture, quickstart, ingestion rules
- `tests/`
  - unit, phase, and integration tests
- `artifacts/`
  - outputs, staging, manifest files

===

What the harness already enforces

- protocol-based NotebookLM boundary
- typed runner errors
- typed flow phases
- staged writes + per-run manifest
- deterministic index rebuilding
- fake-client full-flow integration tests
- Jinja2 template rendering
- parser fallback when NotebookLM output has no comparison table
- ruff + mypy + pytest + coverage gate
- GitHub Actions on ubuntu-latest and macos-latest

===

When is this useful?

- policy comparison research
- vendor analysis
- education, healthcare, or enterprise AI governance research
- building an Obsidian-based personal knowledge base
- any repeatable research-to-knowledge workflow

===

License

See [LICENSE](./LICENSE).
