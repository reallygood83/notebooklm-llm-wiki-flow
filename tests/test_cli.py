import json

from typer.testing import CliRunner

from notebooklm_llm_wiki_flow.cli import app


def test_plan_policy_compare_outputs_builtin_sources():
    result = CliRunner().invoke(app, ["plan-policy-compare", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert any("anthropic.com/legal/commercial-terms" in url for url in payload["sources"])
    assert payload["workflow"] == "policy-compare"
