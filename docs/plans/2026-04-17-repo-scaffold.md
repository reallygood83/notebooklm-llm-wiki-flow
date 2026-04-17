# notebooklm-llm-wiki-flow scaffold implementation plan

> For Hermes: Use subagent-driven-development skill to implement this plan task-by-task.

Goal: create a portable GitHub-ready repository that can bootstrap NotebookLM, capture artifacts, and structure them into an Obsidian-friendly LLM Wiki workflow.

Architecture: lightweight Python CLI + shell bootstrap + opinionated LLM Wiki prompt/config/templates. NotebookLM integration is adapter-driven, while wiki quality is enforced through high-signal extraction rules.

Tech stack: Python 3.11+, Typer, PyYAML, pytest, shell bootstrap, qmd, notebooklm-py.
