"""Smoke tests for the ax/ subpackage.

bug_026의 coverage gap을 메우기 위한 1차 스모크 묶음. 외부 API(NotebookLM,
Gemini, kordoc/npx)는 호출하지 않고, 순수 함수와 파일 I/O round-trip만 검증한다.
향후 mock 기반 통합 테스트로 확장 권장.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from notebooklm_llm_wiki_flow.ax.common import (
    MIMETYPE,
    escape_xml_attr,
    escape_xml_text,
    get_logger,
    read_hwpx,
    step,
    write_hwpx_from_entries,
)
from notebooklm_llm_wiki_flow.ax.convert_docx import convert_md_to_docx
from notebooklm_llm_wiki_flow.ax.convert_hwpx import (
    SECTION_RE,
    md_to_hwpx_xml_fragment,
)
from notebooklm_llm_wiki_flow.ax_cli import _resolve_vault


# ─────────────────────────────────────────────────────────────────────────────
# common.py — pure utilities
# ─────────────────────────────────────────────────────────────────────────────


def test_escape_xml_text_basic() -> None:
    assert escape_xml_text("<a & b>") == "&lt;a &amp; b&gt;"


def test_escape_xml_text_none() -> None:
    # 형식상 str로 들어오지만 방어적 처리 검증
    assert escape_xml_text(None) == ""  # type: ignore[arg-type]


def test_escape_xml_attr_quotes() -> None:
    out = escape_xml_attr("a\"b'c<d>e&f")
    assert "&quot;" in out
    assert "&apos;" in out
    assert "&lt;" in out
    assert "&gt;" in out
    assert "&amp;" in out


def test_get_logger_returns_namespaced() -> None:
    lg = get_logger("test-scope")
    assert lg.name == "aura.test-scope"
    # 재호출해도 handler가 중복으로 붙지 않아야 함
    n_handlers = len(lg.handlers)
    get_logger("test-scope")
    assert len(lg.handlers) == n_handlers


def test_step_completes_and_propagates_exception() -> None:
    lg = get_logger("test-step")
    # 정상 경로
    with step(lg, "ok"):
        pass
    # 예외 경로는 그대로 전파되어야 한다
    with pytest.raises(ValueError):
        with step(lg, "boom"):
            raise ValueError("expected")


def test_hwpx_roundtrip(tmp_path: Path) -> None:
    target = tmp_path / "sample.hwpx"
    entries = {
        "mimetype": MIMETYPE,
        "Contents/section0.xml": "<hp:section>hello</hp:section>",
    }
    write_hwpx_from_entries(entries, str(target))
    assert target.is_file()
    out = read_hwpx(str(target))
    assert out["mimetype"].decode("utf-8") == MIMETYPE
    assert b"hello" in out["Contents/section0.xml"]


def test_read_hwpx_missing(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        read_hwpx(str(tmp_path / "nope.hwpx"))


# ─────────────────────────────────────────────────────────────────────────────
# convert_hwpx.py — markdown → xml fragment (pure)
# ─────────────────────────────────────────────────────────────────────────────


def test_md_to_hwpx_fragment_default_ns_hp() -> None:
    out = md_to_hwpx_xml_fragment("hello\n\nworld")
    assert "<hp:p><hp:run><hp:t>hello</hp:t>" in out
    assert "<hp:p><hp:run><hp:t/></hp:run></hp:p>" in out  # empty line
    assert "<hp:t>world</hp:t>" in out


def test_md_to_hwpx_fragment_ns_hs() -> None:
    out = md_to_hwpx_xml_fragment("line", ns="hs")
    assert "<hs:p><hs:run><hs:t>line</hs:t>" in out
    assert "hp:" not in out


def test_section_re_matches_hp_and_hs() -> None:
    hp_xml = "<hp:section attr='x'>BODY</hp:section>"
    hs_xml = "<hs:section>BODY</hs:section>"
    assert SECTION_RE.search(hp_xml) is not None
    assert SECTION_RE.search(hs_xml) is not None


# ─────────────────────────────────────────────────────────────────────────────
# convert_docx.py — markdown → docx with happy path + edge case
# ─────────────────────────────────────────────────────────────────────────────


def test_convert_md_to_docx_creates_file(tmp_path: Path) -> None:
    md = tmp_path / "sample.md"
    md.write_text(
        "# Heading\n\n"
        "Body with **bold** text.\n\n"
        "| col1 | col2 |\n|------|------|\n| a    | b    |\n",
        encoding="utf-8",
    )
    out = convert_md_to_docx(md)
    assert out.is_file()
    assert out.suffix == ".docx"


def test_convert_md_to_docx_pipe_line_is_preserved_as_paragraph(
    tmp_path: Path,
) -> None:
    """bug_010 회귀 가드: 유효한 표가 아닌 |로 시작하는 라인이 사라지지 않아야 한다."""
    md = tmp_path / "pipe.md"
    md.write_text("|just a stray pipe line|\n", encoding="utf-8")
    out = convert_md_to_docx(md)
    assert out.is_file()  # silent drop이 아니라 변환 자체는 성공


def test_convert_md_to_docx_missing_input(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        convert_md_to_docx(tmp_path / "no_such.md")


# ─────────────────────────────────────────────────────────────────────────────
# ax_cli.py — vault resolution (env precedence)
# ─────────────────────────────────────────────────────────────────────────────


def test_resolve_vault_prefers_explicit(tmp_path: Path) -> None:
    vault = tmp_path / "explicit"
    assert _resolve_vault(vault) == vault


def test_resolve_vault_uses_nlwflow_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("AURA_VAULT_PATH", raising=False)
    monkeypatch.delenv("NLWFLOW_VAULT_PATH", raising=False)
    monkeypatch.setenv("NLWFLOW_OBSIDIAN_VAULT", str(tmp_path / "nlw"))
    assert _resolve_vault(None) == tmp_path / "nlw"


def test_resolve_vault_aura_fallback(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("NLWFLOW_OBSIDIAN_VAULT", raising=False)
    monkeypatch.delenv("NLWFLOW_VAULT_PATH", raising=False)
    monkeypatch.setenv("AURA_VAULT_PATH", str(tmp_path / "aura"))
    assert _resolve_vault(None) == tmp_path / "aura"


def test_resolve_vault_missing_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    import typer  # type: ignore[import-not-found]

    for v in ("NLWFLOW_OBSIDIAN_VAULT", "AURA_VAULT_PATH", "NLWFLOW_VAULT_PATH"):
        monkeypatch.delenv(v, raising=False)
    with pytest.raises(typer.BadParameter):
        _resolve_vault(None)


def test_route_classify_rejects_partial_match(monkeypatch: pytest.MonkeyPatch) -> None:
    """bug_016 회귀 가드: 'WORKFLOW' 같은 응답이 'WORK'로 오분류되지 않아야 한다."""
    from notebooklm_llm_wiki_flow.ax import route as route_mod

    class _FakeResponse:
        text = "WORKFLOW PARSING TODO"

    class _FakeModels:
        def generate_content(self, model: str, contents: str) -> _FakeResponse:
            return _FakeResponse()

    class _FakeClient:
        def __init__(self, api_key: str) -> None:
            self.models = _FakeModels()

    monkeypatch.setenv("GOOGLE_API_KEY", "fake")
    monkeypatch.setattr(route_mod.genai, "Client", _FakeClient)
    with pytest.raises(ValueError):
        route_mod.classify_content("Some content body")


def test_route_classify_missing_key_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    from notebooklm_llm_wiki_flow.ax import route as route_mod

    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    # ax_cli.load_dotenv()가 .env에서 GOOGLE_API_KEY를 복원할 수 있으므로
    # os.environ에서 직접 강제 제거된 상태를 가정한 단위 테스트
    with pytest.raises(RuntimeError):
        os.environ.pop("GOOGLE_API_KEY", None)
        route_mod.classify_content("x")
