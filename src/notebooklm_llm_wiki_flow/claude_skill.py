from __future__ import annotations

from importlib import resources
from pathlib import Path

SKILL_FILENAME = "note-wiki.md"
_PACKAGE_SKILLS = "notebooklm_llm_wiki_flow.skills"
_PACKAGE_PROMPTS = "notebooklm_llm_wiki_flow.prompts"
PROMPT_FILENAMES = ("llm_wiki_priority.md", "policy_compare.md")
PROMPTS_SUBDIR = "nlwflow-prompts"


def _read_packaged_skill() -> str:
    return (
        resources.files(_PACKAGE_SKILLS)
        .joinpath(SKILL_FILENAME)
        .read_text(encoding="utf-8")
    )


def _read_packaged_prompt(name: str) -> str:
    return (
        resources.files(_PACKAGE_PROMPTS)
        .joinpath(name)
        .read_text(encoding="utf-8")
    )


def install_claude_skill(
    target_dir: str | Path | None = None,
    *,
    force: bool = False,
    source_path: str | Path | None = None,
) -> Path:
    """note-wiki 스킬과 동반 프롬프트 2종을 함께 설치한다.

    프롬프트는 ``<target_dir>/nlwflow-prompts/`` 아래에 동봉되어, 스킬 step 0이
    실행 디렉터리와 무관하게 동일 경로에서 프롬프트를 읽도록 보장한다.
    """
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

    # 프롬프트 동봉 설치 (스킬 step 0이 외부 디렉터리에서도 작동하도록)
    # force=False 일 때 기존 프롬프트가 있으면 보존(사용자 편집본을 잃지 않기 위함).
    prompts_dir = root / PROMPTS_SUBDIR
    prompts_dir.mkdir(parents=True, exist_ok=True)
    for name in PROMPT_FILENAMES:
        prompt_target = prompts_dir / name
        if prompt_target.exists() and not force:
            continue
        prompt_text = _read_packaged_prompt(name)
        prompt_target.write_text(prompt_text, encoding="utf-8")

    return dest
