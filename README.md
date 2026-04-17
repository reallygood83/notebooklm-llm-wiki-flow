# notebooklm-llm-wiki-flow

One GitHub repository to bootstrap a reusable NotebookLM → LLM Wiki → Obsidian → qmd workflow.

This repository is designed for people who want:
- NotebookLM for source-grounded research and artifact generation
- LLM Wiki as the persistent knowledge structure
- Obsidian as the editing and browsing surface
- qmd as the retrieval layer over the vault

## What this scaffold already gives you

- Python CLI scaffold (`nlwflow`)
- bootstrap script that installs the core local dependencies
- example config and example policy-comparison workflow inputs
- report and mind-map parsing helpers
- wiki note rendering helper
- LLM Wiki priority rules so the most important claims survive ingestion
- GitHub Actions test workflow
- pytest coverage for the core parsing/rendering scaffold

## Repository layout

- `src/notebooklm_llm_wiki_flow/` — Python package and CLI
- `scripts/bootstrap.sh` — local setup for Python env, notebooklm-py, Playwright, and qmd
- `config/project.example.yaml` — user-editable local config
- `config/prompts/` — workflow prompts and LLM Wiki priority rules
- `examples/` — example workflow inputs
- `templates/` — markdown templates for future wiki generation
- `docs/` — architecture, quickstarts, ingestion rules, and implementation plan
- `tests/` — parser and CLI smoke tests

## Quick start

1. Clone the repo.
2. Run `./scripts/bootstrap.sh`
3. Run `notebooklm login`
4. Run `./.venv/bin/nlwflow init-config`
5. Run `./.venv/bin/nlwflow doctor --json`
6. Run `./.venv/bin/nlwflow plan-policy-compare --json`

## Why the LLM Wiki quality rules matter

A bad workflow turns NotebookLM artifacts into generic summary dumps.
A good workflow preserves the decision-relevant claims.

This scaffold therefore prioritizes:
- explicit obligations and prohibitions
- retention numbers and time windows
- student and minor safety rules
- human review requirements for high-stakes decisions
- enterprise controls such as SSO, audit logs, retention controls
- ownership, indemnity, and legal risk allocation

Those rules live in:
- `config/prompts/llm_wiki_priority.md`
- `docs/llm-wiki-ingestion-standard.md`

## Current CLI commands

- `nlwflow doctor` — environment and path checks
- `nlwflow init-config` — write a starter config file
- `nlwflow plan-policy-compare` — emit a built-in Anthropic vs OpenAI policy-comparison source pack
- `nlwflow score-report REPORT.md` — score and extract high-signal sections from a NotebookLM report

## Intended end-state workflow

1. feed official URLs/PDFs into NotebookLM
2. generate report, mind map, and Q&A artifacts
3. save raw artifacts with provenance
4. extract high-signal claims
5. create or update entity/comparison/query pages in the wiki
6. index the vault with qmd
7. reuse the compiled knowledge in future research

## Notes

- This repo assumes local-first execution.
- NotebookLM authentication remains a browser login step.
- The scaffold is ready for GitHub, but does not automatically publish your local work.
- The next implementation step is to wire the full NotebookLM export + wiki write loop into the CLI.
