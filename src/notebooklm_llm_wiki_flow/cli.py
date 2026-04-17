from __future__ import annotations

import json
import shutil
from pathlib import Path

import typer
from rich import print

from . import __version__
from .config import load_config
from .flow import run_from_yaml, run_plan, run_policy_compare
from .models import WorkflowConfig
from .obsidian_kit import install_obsidian_kit
from .report_parser import extract_report_highlights
from .workflows import build_note_wiki_plan, build_policy_compare_plan

app = typer.Typer(help="NotebookLM → LLM Wiki → Obsidian workflow helper")


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"nlwflow {__version__}")
        raise typer.Exit()


@app.callback()
def _root(
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        help="Show version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
) -> None:
    """nlwflow: NotebookLM → LLM Wiki → Obsidian workflow helper."""


def _resolved_path(value: Path | None) -> Path | None:
    if value is None:
        return None
    return value.expanduser().resolve()


def _with_paths(cfg: WorkflowConfig, *, obsidian_vault: Path, wiki_path: Path) -> WorkflowConfig:
    return WorkflowConfig(
        project_name=cfg.project_name,
        obsidian_vault=obsidian_vault,
        wiki_path=wiki_path,
        qmd_collection=cfg.qmd_collection,
        artifacts_root=cfg.artifacts_root,
        notebooklm_command=cfg.notebooklm_command,
        qmd_command=cfg.qmd_command,
    )


def _resolve_note_wiki_config(
    *,
    base_cfg: WorkflowConfig,
    vault: Path | None,
    wiki_path: Path | None,
) -> WorkflowConfig:
    resolved_vault = _resolved_path(vault) or base_cfg.obsidian_vault
    if not resolved_vault.exists():
        response = typer.prompt(
            "Obsidian vault path not found. Enter vault path",
            default=str(resolved_vault),
        )
        resolved_vault = Path(response).expanduser().resolve()

    default_wiki = resolved_vault / "LLM-Wiki"
    resolved_wiki = _resolved_path(wiki_path) or base_cfg.wiki_path
    if not resolved_wiki.exists():
        response = typer.prompt(
            "LLM Wiki path not found. Enter wiki path",
            default=str(default_wiki),
        )
        resolved_wiki = Path(response).expanduser().resolve()

    return _with_paths(
        base_cfg,
        obsidian_vault=resolved_vault,
        wiki_path=resolved_wiki,
    )


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


@app.command('run-from-yaml')
def run_from_yaml_command(
    workflow_path: Path,
    config: str | None = typer.Option(None, help="Optional config file"),
    dry_run: bool = typer.Option(False, '--dry-run', help='Print the loaded workflow without executing NotebookLM'),
    json_output: bool = typer.Option(False, '--json', help='Emit JSON'),
    no_qmd_update: bool = typer.Option(False, '--no-qmd-update', help='Skip qmd update after writing notes'),
) -> None:
    payload = run_from_yaml(workflow_path, config, dry_run=dry_run, qmd_update_enabled=not no_qmd_update)
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False))
        raise typer.Exit()

    print(json.dumps(payload, ensure_ascii=False, indent=2))


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


@app.command('note-wiki')
def note_wiki_command(
    prompt: str,
    config: str | None = typer.Option(None, help="Optional config file"),
    source: list[str] | None = typer.Option(None, '--source', help='Additional source URL'),
    title: str | None = typer.Option(None, '--title', help='Optional note title'),
    vault: Path | None = typer.Option(None, '--vault', help='Override Obsidian vault path'),
    wiki_path: Path | None = typer.Option(None, '--wiki-path', help='Override LLM Wiki path'),
    dry_run: bool = typer.Option(False, '--dry-run', help='Print generated plan without executing NotebookLM'),
    json_output: bool = typer.Option(False, '--json', help='Emit JSON'),
    no_qmd_update: bool = typer.Option(False, '--no-qmd-update', help='Skip qmd update after writing notes'),
) -> None:
    base_cfg = load_config(config) if config else load_config()
    resolved_cfg = _resolve_note_wiki_config(
        base_cfg=base_cfg,
        vault=vault,
        wiki_path=wiki_path,
    )
    plan = build_note_wiki_plan(prompt, title=title, sources=source or [])
    if not plan['sources'] and not dry_run:
        raise typer.BadParameter(
            'No source URLs found. Include URLs in the prompt or pass one or more --source values.',
        )

    payload = run_plan(
        plan,
        config_path=config,
        cfg_override=resolved_cfg,
        dry_run=dry_run,
        qmd_update_enabled=not no_qmd_update,
    )
    payload['resolved_config'] = {
        'obsidian_vault': str(resolved_cfg.obsidian_vault),
        'wiki_path': str(resolved_cfg.wiki_path),
    }
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
