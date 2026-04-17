from __future__ import annotations

import json
import shutil
from pathlib import Path

import typer
from rich import print

from .config import load_config
from .flow import run_policy_compare
from .obsidian_kit import install_obsidian_kit
from .report_parser import extract_report_highlights
from .workflows import build_policy_compare_plan

app = typer.Typer(help="NotebookLM → LLM Wiki → Obsidian workflow helper")


@app.command()
def doctor(config: str | None = typer.Option(None, help="Optional config file"), json_output: bool = typer.Option(False, '--json', help='Emit JSON')) -> None:
    cfg = load_config(config) if config else load_config()
    payload = {
        "notebooklm": shutil.which(cfg.notebooklm_command) is not None,
        "qmd": shutil.which(cfg.qmd_command) is not None,
        "obsidian_vault_exists": cfg.obsidian_vault.exists(),
        "wiki_path_exists": cfg.wiki_path.exists(),
        "qmd_collection": cfg.qmd_collection,
    }
    if json_output:
        typer.echo(json.dumps(payload))
        raise typer.Exit()

    for key, value in payload.items():
        print(f"- {key}: {value}")


@app.command('init-config')
def init_config(target: Path = typer.Argument(Path('config/project.yaml'))) -> None:
    source = Path(__file__).resolve().parents[2] / 'config' / 'project.example.yaml'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(source.read_text(encoding='utf-8'), encoding='utf-8')
    print(f"Wrote config to {target}")


@app.command('install-obsidian-kit')
def install_obsidian_kit_command(vault: Path = typer.Option(..., '--vault', help='Target Obsidian vault path'), json_output: bool = typer.Option(False, '--json', help='Emit JSON')) -> None:
    created = install_obsidian_kit(vault)
    payload = {'vault': str(vault), 'created': created}
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False))
        raise typer.Exit()
    print(json.dumps(payload, ensure_ascii=False, indent=2))


@app.command('plan-policy-compare')
def plan_policy_compare(json_output: bool = typer.Option(False, '--json', help='Emit JSON')) -> None:
    plan = build_policy_compare_plan()
    if json_output:
        typer.echo(json.dumps(plan))
        raise typer.Exit()

    print(f"Title: {plan['title']}")
    print("Sources:")
    for source in plan['sources']:
        print(f"- {source}")


@app.command('run-policy-compare')
def run_policy_compare_command(
    config: str | None = typer.Option(None, help="Optional config file"),
    dry_run: bool = typer.Option(False, '--dry-run', help='Print the plan without executing NotebookLM'),
    json_output: bool = typer.Option(False, '--json', help='Emit JSON'),
    no_qmd_update: bool = typer.Option(False, '--no-qmd-update', help='Skip qmd update after writing notes'),
) -> None:
    payload = run_policy_compare(config, dry_run=dry_run, qmd_update_enabled=not no_qmd_update)
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False))
        raise typer.Exit()

    print(json.dumps(payload, ensure_ascii=False, indent=2))


@app.command('score-report')
def score_report(report_path: Path, json_output: bool = typer.Option(False, '--json', help='Emit JSON')) -> None:
    highlights = extract_report_highlights(report_path.read_text(encoding='utf-8'))
    payload = {
        "title": highlights.title,
        "sections": [section.title for section in highlights.sections],
        "bullets": highlights.bullets,
    }
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False))
        raise typer.Exit()

    print(f"Title: {payload['title']}")
    print("Sections:")
    for section in payload['sections']:
        print(f"- {section}")
    print("Bullets:")
    for bullet in payload['bullets']:
        print(f"- {bullet}")


if __name__ == '__main__':
    app()
