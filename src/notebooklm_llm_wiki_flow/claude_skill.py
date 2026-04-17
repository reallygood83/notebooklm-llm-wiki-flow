from __future__ import annotations

from importlib import resources
from pathlib import Path

SKILL_FILENAME = "note-wiki.md"
_PACKAGE_SKILLS = "notebooklm_llm_wiki_flow.skills"


def _read_packaged_skill() -> str:
    return (
        resources.files(_PACKAGE_SKILLS)
        .joinpath(SKILL_FILENAME)
        .read_text(encoding="utf-8")
    )


def install_claude_skill(
    target_dir: str | Path | None = None,
    *,
    force: bool = False,
    source_path: str | Path | None = None,
) -> Path:
    if source_path is not None:
        src = Path(source_path).expanduser().resolve()
        if not src.is_file():
            raise FileNotFoundError(f"Skill source not found: {src}")
        content = src.read_text(encoding="utf-8")
    else:
        content = _read_packaged_skill()

    root = (
        Path(target_dir).expanduser().resolve()
        if target_dir is not None
        else Path.home() / ".claude" / "commands"
    )
    root.mkdir(parents=True, exist_ok=True)
    dest = root / SKILL_FILENAME
    if dest.exists() and not force:
        raise FileExistsError(
            f"Skill already installed at {dest}. Use force=True to overwrite."
        )
    dest.write_text(content, encoding="utf-8")
    return dest
