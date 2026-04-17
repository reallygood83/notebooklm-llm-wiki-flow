from pathlib import Path
from typing import Any


class FakeNotebookLMClient:
    def create_notebook(self, title: str) -> dict[str, Any]:
        return {"id": "nb-demo", "title": title}

    def add_source(self, notebook_id: str, source: str) -> dict[str, Any]:
        return {"id": f"src-{source.rsplit('/', 1)[-1]}", "url": source}

    def wait_source(self, notebook_id: str, source_id: str, timeout: int = 300) -> dict[str, Any]:
        return {"id": source_id, "status": "ready", "timeout": timeout}

    def generate_report(self, notebook_id: str, report_append: str) -> dict[str, Any]:
        return {"task_id": "task-report"}

    def wait_artifact(self, notebook_id: str, artifact_id: str, timeout: int = 900) -> dict[str, Any]:
        return {"id": artifact_id, "status": "ready", "timeout": timeout}

    def generate_mind_map(self, notebook_id: str) -> dict[str, Any]:
        return {"note_id": "mindmap-1"}

    def ask(self, notebook_id: str, question: str) -> dict[str, Any]:
        return {"answer": "- [ ] Keep human review in the loop"}

    def download_report(self, notebook_id: str, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            "# Demo report\n\n## Findings\n\n| Feature | OpenAI | Anthropic |\n| --- | --- | --- |\n| Review | Human review | Human review |\n",
            encoding="utf-8",
        )

    def download_mind_map(self, notebook_id: str, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text('{"note_id":"mindmap-1"}', encoding="utf-8")
