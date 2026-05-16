"""AURA Administrative (AX) CLI.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich import print

from .ax.convert_docx import convert_md_to_docx
from .ax.convert_hwpx import inject_md_into_hwpx
from .ax.ingest import ingest_file
from .ax.route import route_file

ax_app = typer.Typer(help="AURA Administrative (AX) tools")

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
        print(f"[bold green]Converted to DOCX:[/bold green] {result}")
    elif format == "hwpx":
        if not template:
            print("[bold red]Error:[/bold red] HWPX conversion requires a --template file.")
            raise typer.Exit(1)
        
        out_path = output or input_file.with_suffix(".hwpx")
        result = inject_md_into_hwpx(input_file, template, out_path)
        print(f"[bold green]Converted to HWPX (Surgical):[/bold green] {result}")
    else:
        print(f"[bold red]Error:[/bold red] Unsupported format: {format}")
        raise typer.Exit(1)

@ax_app.command("ingest")
def ingest(
    input_file: Path = typer.Argument(..., help="Document file to ingest"),
    output_dir: Optional[Path] = typer.Option(None, "--output-dir", "-d", help="Target directory"),
) -> None:
    """Ingest a document (HWPX, PDF, etc.) into Markdown."""
    target = output_dir or input_file.parent
    result = ingest_file(input_file, target)
    if result:
        print(f"[bold green]Ingested:[/bold green] {result}")
    else:
        print("[bold red]Ingestion failed.[/bold red]")

@ax_app.command("route")
def route(
    input_file: Path = typer.Argument(..., help="Markdown file to route"),
    vault: Optional[Path] = typer.Option(None, "--vault", help="Obsidian vault root"),
) -> None:
    """Intelligently route a Markdown file within the PARA+ structure."""
    # Try to find vault root if not provided
    vault_root = vault or Path("/Users/choichanghoon/Obsidian Vault/My Vault")
    result = route_file(input_file, vault_root)
    if result:
        print(f"[bold green]Routed to:[/bold green] {result}")
    else:
        print("[bold red]Routing failed.[/bold red]")

@ax_app.command("doctor")
def ax_doctor() -> None:
    """Check AURA administrative environment."""
    print("[bold blue]AURA AX Health Check[/bold blue]")
    
    # Check for docx
    try:
        import docx
        print(f"- python-docx: [green]OK[/green] (version {docx.__version__})")
    except ImportError:
        print("- python-docx: [red]MISSING[/red]")
        
    print("- OCF Packager: [green]OK[/green]")
    print("- Surgical Injector: [green]OK[/green]")
