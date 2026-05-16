import os
from pathlib import Path
from typing import Optional

import typer
from dotenv import load_dotenv
from google import genai
from rich.console import Console
from rich.markdown import Markdown

app = typer.Typer(help="AURA-Gemini CLI: Direct access to Gemini intelligence from terminal")
console = Console()

def get_api_key():
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        console.print("[bold red]Error:[/bold red] GOOGLE_API_KEY not found in .env file.")
        console.print("Please add 'GOOGLE_API_KEY=your_key_here' to your .env file.")
        raise typer.Exit(code=1)
    return api_key

@app.command()
def chat(
    prompt: str = typer.Argument(..., help="Question or instruction for Gemini"),
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="Optional file to read and include in context"),
    model: str = typer.Option("gemini-flash-latest", "--model", "-m", help="Gemini model to use"),
    stream: bool = typer.Option(True, "--no-stream", help="Disable streaming response"),
):
    """Ask Gemini anything. Supports file context."""
    api_key = get_api_key()
    client = genai.Client(api_key=api_key)

    full_prompt = prompt
    if file:
        if not file.exists():
            console.print(f"[bold red]Error:[/bold red] File not found: {file}")
            raise typer.Exit(code=1)
        content = file.read_text(encoding="utf-8")
        full_prompt = f"Context from file {file.name}:\n\n{content}\n\n---\n\nUser Question: {prompt}"

    try:
        if stream:
            response = client.models.generate_content_stream(model=model, contents=full_prompt)
            console.print(f"\n[bold blue]Hermes:[/bold blue]")
            accumulated_text = ""
            for chunk in response:
                chunk_text = chunk.text or ""
                accumulated_text += chunk_text
                console.print(chunk_text, end="")
            console.print("\n")
        else:
            response = client.models.generate_content(model=model, contents=full_prompt)
            console.print(f"\n[bold blue]Hermes:[/bold blue]")
            console.print(Markdown(response.text))
    except Exception as e:
        console.print(f"[bold red]API Error:[/bold red] {str(e)}")
        raise typer.Exit(code=1)

@app.command()
def version():
    """Show version info."""
    console.print("AURA-Gemini CLI v0.1.0 (Hermes Edition)")

if __name__ == "__main__":
    app()
