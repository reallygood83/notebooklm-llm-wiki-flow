from pathlib import Path

import pytest

from notebooklm_llm_wiki_flow.claude_skill import (
    SKILL_FILENAME,
    _read_packaged_skill,
    install_claude_skill,
)


def test_packaged_skill_is_readable():
    content = _read_packaged_skill()
    assert "description:" in content
    assert "$ARGUMENTS" in content
    assert "nlwflow note-wiki" in content


def test_repo_and_packaged_skill_match():
    repo_root = Path(__file__).resolve().parents[1]
    repo_copy = repo_root / ".claude" / "commands" / SKILL_FILENAME
    assert repo_copy.is_file(), "project-level slash command file missing"
    assert repo_copy.read_text(encoding="utf-8") == _read_packaged_skill()


def test_install_claude_skill_writes_expected_file(tmp_path: Path):
    installed = install_claude_skill(target_dir=tmp_path)
    assert installed == tmp_path / SKILL_FILENAME
    assert installed.read_text(encoding="utf-8") == _read_packaged_skill()


def test_install_claude_skill_refuses_to_overwrite_without_force(tmp_path: Path):
    install_claude_skill(target_dir=tmp_path)
    with pytest.raises(FileExistsError):
        install_claude_skill(target_dir=tmp_path)


def test_install_claude_skill_force_overwrites(tmp_path: Path):
    first = install_claude_skill(target_dir=tmp_path)
    first.write_text("stale", encoding="utf-8")
    install_claude_skill(target_dir=tmp_path, force=True)
    assert first.read_text(encoding="utf-8") == _read_packaged_skill()
