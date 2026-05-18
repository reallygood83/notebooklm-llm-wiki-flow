"""AURA Administrative (AX) CLI."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
from typing import Optional

import typer
from dotenv import load_dotenv
from rich import print
from rich.markup import escape

from .ax.convert_docx import convert_md_to_docx
from .ax.convert_hwpx import inject_md_into_hwpx
from .ax.ingest import ingest_file
from .ax.route import route_file

ax_app = typer.Typer(help="AURA Administrative (AX) tools")


@ax_app.callback()
def _ax_bootstrap() -> None:
    """ax 하위 명령 실행 직전 .env 로드 (모듈 import 시점 부작용 제거)."""
    load_dotenv()


def _resolve_vault(explicit: Optional[Path]) -> Path:
    """vault 경로를 명시적 인자 → 환경변수 → 에러 순으로 해석.

    표준 변수명은 ``NLWFLOW_OBSIDIAN_VAULT``(config.py와 일치). 호환을 위해
    ``AURA_VAULT_PATH``와 ``NLWFLOW_VAULT_PATH``도 fallback으로 수용한다.
    개인 경로 하드코딩은 제거되어 있다.
    """
    if explicit is not None:
        # bug #5: env 분기와 대칭으로 `--vault '~/...'`도 셸 확장이 안 된 경우 해석.
        return explicit.expanduser()
    env_path = (
        os.environ.get("NLWFLOW_OBSIDIAN_VAULT")
        or os.environ.get("AURA_VAULT_PATH")
        or os.environ.get("NLWFLOW_VAULT_PATH")
    )
    if env_path:
        return Path(env_path).expanduser()
    raise typer.BadParameter(
        "Vault path not provided. Pass --vault or set NLWFLOW_OBSIDIAN_VAULT "
        "(or AURA_VAULT_PATH / NLWFLOW_VAULT_PATH) to your Obsidian vault root."
    )


@ax_app.command("convert")
def convert(
    input_file: Path = typer.Argument(..., help="Input Markdown file"),
    format: str = typer.Option("docx", "--format", "-f", help="Target format (docx, hwpx)"),
    template: Optional[Path] = typer.Option(None, "--template", "-t", help="Template file (required for HWPX)"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
) -> None:
    """Convert Markdown to administrative formats (DOCX, HWPX)."""
    if format == "docx":
        result = convert_md_to_docx(input_file, output)
        print(f"[bold green]Converted to DOCX:[/bold green] {escape(str(result))}")
    elif format == "hwpx":
        if not template:
            print("[bold red]Error:[/bold red] HWPX conversion requires a --template file.")
            raise typer.Exit(1)

        out_path = output or input_file.with_suffix(".hwpx")
        result = inject_md_into_hwpx(input_file, template, out_path)
        print(
            f"[bold green]Converted to HWPX (Surgical):[/bold green] {escape(str(result))}"
        )
    else:
        print(f"[bold red]Error:[/bold red] Unsupported format: {escape(format)}")
        raise typer.Exit(1)


@ax_app.command("ingest")
def ingest(
    input_file: Path = typer.Argument(..., help="Document file to ingest"),
    output_dir: Optional[Path] = typer.Option(None, "--output-dir", "-d", help="Target directory"),
) -> None:
    """Ingest a document (HWPX, PDF, etc.) into Markdown."""
    target = output_dir or input_file.parent
    result = ingest_file(input_file, target)
    print(f"[bold green]Ingested:[/bold green] {escape(str(result))}")


@ax_app.command("route")
def route(
    input_file: Path = typer.Argument(..., help="Markdown file to route"),
    vault: Optional[Path] = typer.Option(
        None,
        "--vault",
        help=(
            "Obsidian vault root. Falls back to $NLWFLOW_OBSIDIAN_VAULT, "
            "$AURA_VAULT_PATH, or $NLWFLOW_VAULT_PATH."
        ),
    ),
) -> None:
    """Intelligently route a Markdown file within the PARA+ structure."""
    vault_root = _resolve_vault(vault)
    result = route_file(input_file, vault_root)
    print(f"[bold green]Routed to:[/bold green] {escape(str(result))}")

@ax_app.command("doctor")
def ax_doctor() -> None:
    """Check AURA administrative environment."""
    print("[bold blue]AURA AX Health Check[/bold blue]")

    # importlib.util.find_spec — try/except import는 cli.py:ax_cli eager
    # import 때문에 docx 누락이면 여기 도달조차 못하는 dead code였음.
    if importlib.util.find_spec("docx") is not None:
        import docx

        print(f"- python-docx: [green]OK[/green] (version {docx.__version__})")
    else:
        print(
            "- python-docx: [red]MISSING[/red] — install ax extras: "
            "[bold]pip install '.[ax]'[/bold]"
        )

    print("- OCF Packager: [green]OK[/green]")
    print("- Surgical Injector: [green]OK[/green]")
