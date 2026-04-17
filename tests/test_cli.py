import json

from typer.testing import CliRunner

from notebooklm_llm_wiki_flow import __version__
from notebooklm_llm_wiki_flow.cli import app


def test_version_flag_prints_version():
    result = CliRunner().invoke(app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout


def test_plan_policy_compare_outputs_builtin_sources():
    result = CliRunner().invoke(app, ["plan-policy-compare", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert any("anthropic.com/legal/commercial-terms" in url for url in payload["sources"])
    assert payload["workflow"] == "policy-compare"


def test_run_policy_compare_dry_run_returns_plan_payload():
    result = CliRunner().invoke(app, ["run-policy-compare", "--dry-run", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["mode"] == "dry-run"
    assert payload["plan"]["workflow"] == "policy-compare"
    assert any("openai.com/enterprise-privacy" in url for url in payload["plan"]["sources"])


def test_note_wiki_dry_run_returns_generated_plan_with_prompt_sources(tmp_path):
    vault_path = tmp_path / "Vault"
    vault_path.mkdir()
    result = CliRunner().invoke(
        app,
        [
            "note-wiki",
            "Summarize https://example.com/a for school admins",
            "--vault",
            str(vault_path),
            "--wiki-path",
            str(vault_path),
            "--dry-run",
            "--json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["mode"] == "dry-run"
    assert payload["plan"]["workflow"] == "note-wiki"
    assert payload["plan"]["sources"] == ["https://example.com/a"]


def test_note_wiki_prompts_for_vault_path_when_config_path_missing(tmp_path):
    config_path = tmp_path / "project.yaml"
    config_path.write_text(
        "project_name: test\nobsidian_vault: /path/does/not/exist\nwiki_path: /path/does/not/exist/wiki\n",
        encoding="utf-8",
    )
    vault_path = tmp_path / "Vault"
    result = CliRunner().invoke(
        app,
        [
            "note-wiki",
            "Summarize https://example.com/a",
            "--config",
            str(config_path),
            "--dry-run",
            "--json",
        ],
        input=f"{vault_path}\n\n",
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout.splitlines()[-1])
    assert payload["resolved_config"]["obsidian_vault"] == str(vault_path.resolve())
    assert payload["resolved_config"]["wiki_path"] == str((vault_path / 'LLM-Wiki').resolve())
