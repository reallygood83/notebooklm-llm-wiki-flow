import subprocess
from pathlib import Path

import pytest

from notebooklm_llm_wiki_flow import flow
from notebooklm_llm_wiki_flow.models import WorkflowConfig
from notebooklm_llm_wiki_flow.notebooklm_client import (
    NotebookLMClient,
    NotebookLMCommandError,
    NotebookLMTimeoutError,
)
from notebooklm_llm_wiki_flow.runner import NotebookLMRunner
from tests.fakes.fake_notebooklm_client import FakeNotebookLMClient


def test_notebooklm_runner_implements_client_protocol():
    runner = NotebookLMRunner("notebooklm")

    assert isinstance(runner, NotebookLMClient)


def test_notebooklm_runner_wraps_called_process_error_with_step_context(monkeypatch: pytest.MonkeyPatch):
    def fake_run(*args, **kwargs):
        raise subprocess.CalledProcessError(
            1,
            ["notebooklm", "create", "Demo", "--json"],
            stderr="boom",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)
    runner = NotebookLMRunner("notebooklm")

    with pytest.raises(NotebookLMCommandError) as exc_info:
        runner.create_notebook("Demo")

    error = exc_info.value
    assert error.step == "create_notebook"
    assert error.command == ["notebooklm", "create", "Demo", "--json"]
    assert "boom" in str(error)


def test_notebooklm_runner_wraps_invalid_json_with_step_context(monkeypatch: pytest.MonkeyPatch):
    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(args[0], 0, stdout="not-json", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    runner = NotebookLMRunner("notebooklm")

    with pytest.raises(NotebookLMCommandError) as exc_info:
        runner.create_notebook("Demo")

    error = exc_info.value
    assert error.step == "create_notebook"
    assert error.command == ["notebooklm", "create", "Demo", "--json"]
    assert "not-json" in error.stdout


def test_notebooklm_runner_wraps_timeout_with_step_context(monkeypatch: pytest.MonkeyPatch):
    def fake_run(*args, **kwargs):
        raise subprocess.TimeoutExpired(args[0], kwargs["timeout"])

    monkeypatch.setattr(subprocess, "run", fake_run)
    runner = NotebookLMRunner("notebooklm")

    with pytest.raises(NotebookLMTimeoutError) as exc_info:
        runner.wait_source("nb-demo", "src-1", timeout=300)

    error = exc_info.value
    assert error.step == "wait_source"
    assert error.command == ["notebooklm", "source", "wait", "-n", "nb-demo", "src-1", "--timeout", "300", "--json"]
    assert error.timeout_seconds == 305


def test_run_policy_compare_accepts_injected_client(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    wiki_path = tmp_path / "LLM-Wiki"
    wiki_path.mkdir(parents=True)
    (wiki_path / "index.md").write_text(
        "# Index\n\nLast updated: 2026-04-17 | Total pages: 1\n\n## Entities\n\n## Comparisons\n\n## Queries\n",
        encoding="utf-8",
    )
    (wiki_path / "log.md").write_text("# Log\n", encoding="utf-8")
    obsidian_vault = tmp_path / "LearningMaster"
    obsidian_vault.mkdir()
    artifacts_root = tmp_path / "artifacts"

    cfg = WorkflowConfig(
        project_name="test-project",
        obsidian_vault=obsidian_vault,
        wiki_path=wiki_path,
        qmd_collection="learningmaster",
        artifacts_root=artifacts_root,
    )
    monkeypatch.setattr(flow, "load_config", lambda path=None: cfg)

    payload = flow.run_policy_compare(qmd_update_enabled=False, client=FakeNotebookLMClient())

    assert payload["notebook_id"] == "nb-demo"
    assert Path(payload["comparison_page"]).exists()
    assert Path(payload["inbox_note"]).exists()
    assert Path(payload["manifest_path"]).exists()
