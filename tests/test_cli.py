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
