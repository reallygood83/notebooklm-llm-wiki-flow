import json
from pathlib import Path

import pytest

from notebooklm_llm_wiki_flow.persistence import GeneratedFile, persist_generated_outputs


def test_persist_generated_outputs_writes_files_and_manifest(tmp_path: Path):
    artifacts_dir = tmp_path / "artifacts" / "nb-demo"
    wiki_dir = tmp_path / "wiki"

    generated_files = [
        GeneratedFile(
            relative_path="raw/articles/demo-source.md",
            target_path=wiki_dir / "raw/articles/demo-source.md",
            content="# Demo source\n",
        ),
        GeneratedFile(
            relative_path="entities/openai.md",
            target_path=wiki_dir / "entities/openai.md",
            content="# OpenAI\n",
        ),
    ]

    result = persist_generated_outputs(
        notebook_id="nb-demo",
        artifacts_dir=artifacts_dir,
        generated_files=generated_files,
        created_at="2026-04-17",
    )

    assert (wiki_dir / "raw/articles/demo-source.md").read_text(encoding="utf-8") == "# Demo source\n"
    assert (wiki_dir / "entities/openai.md").read_text(encoding="utf-8") == "# OpenAI\n"
    assert result.manifest_path == artifacts_dir / "manifest.json"
    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    assert manifest["notebook_id"] == "nb-demo"
    assert manifest["created_at"] == "2026-04-17"
    assert manifest["staging_dir"].endswith("artifacts/nb-demo/staging")
    assert [item["relative_path"] for item in manifest["files"]] == [
        "raw/articles/demo-source.md",
        "entities/openai.md",
    ]
    assert all(item["sha256"] for item in manifest["files"])


def test_persist_generated_outputs_rolls_back_on_move_failure(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    artifacts_dir = tmp_path / "artifacts" / "nb-demo"
    wiki_dir = tmp_path / "wiki"

    generated_files = [
        GeneratedFile(
            relative_path="raw/articles/demo-source.md",
            target_path=wiki_dir / "raw/articles/demo-source.md",
            content="# Demo source\n",
        ),
        GeneratedFile(
            relative_path="entities/openai.md",
            target_path=wiki_dir / "entities/openai.md",
            content="# OpenAI\n",
        ),
    ]

    import notebooklm_llm_wiki_flow.persistence as persistence

    original_move = persistence.shutil.move
    calls = {"count": 0}

    def flaky_move(src, dst):
        calls["count"] += 1
        if calls["count"] == 2:
            raise RuntimeError("boom")
        return original_move(src, dst)

    monkeypatch.setattr(persistence.shutil, "move", flaky_move)

    with pytest.raises(RuntimeError):
        persist_generated_outputs(
            notebook_id="nb-demo",
            artifacts_dir=artifacts_dir,
            generated_files=generated_files,
            created_at="2026-04-17",
        )

    assert not (wiki_dir / "raw/articles/demo-source.md").exists()
    assert not (wiki_dir / "entities/openai.md").exists()
    assert not (artifacts_dir / "manifest.json").exists()
