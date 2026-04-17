from pathlib import Path

from notebooklm_llm_wiki_flow.log_builder import append_log_entry, build_log_entry


def test_build_log_entry_includes_required_fields():
    entry = build_log_entry(
        title="Demo run",
        notebook_id="nb-demo",
        created_files=["wiki/foo.md"],
        updated_files=["index.md"],
        today="2026-04-17",
    )
    assert "## [2026-04-17] ingest | Demo run" in entry
    assert "Notebook ID: nb-demo" in entry
    assert "Files created:" in entry
    assert "  - wiki/foo.md" in entry
    assert "Files updated:" in entry


def test_append_log_entry_creates_missing_file(tmp_path: Path):
    log_path = tmp_path / "log.md"
    append_log_entry(log_path, "Demo", "nb-1", ["a.md"], None)
    text = log_path.read_text(encoding="utf-8")
    assert "Notebook ID: nb-1" in text
    assert "Files created:" in text


def test_append_log_entry_is_idempotent(tmp_path: Path):
    log_path = tmp_path / "log.md"
    log_path.write_text("# Log\n", encoding="utf-8")
    append_log_entry(log_path, "Demo", "nb-1", ["a.md"])
    first = log_path.read_text(encoding="utf-8")
    append_log_entry(log_path, "Demo", "nb-1", ["a.md"])
    second = log_path.read_text(encoding="utf-8")
    assert first == second
