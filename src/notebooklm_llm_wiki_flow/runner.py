from __future__ import annotations

import json
import subprocess
from pathlib import Path


class NotebookLMRunner:
    def __init__(self, command: str = 'notebooklm') -> None:
        self.command = command

    def _run(self, *args: str) -> str:
        result = subprocess.run(
            [self.command, *args],
            check=True,
            text=True,
            capture_output=True,
        )
        return result.stdout.strip()

    def _run_json(self, *args: str) -> dict:
        return json.loads(self._run(*args))

    def create_notebook(self, title: str) -> dict:
        return self._run_json('create', title, '--json')['notebook']

    def add_source(self, notebook_id: str, source: str) -> dict:
        return self._run_json('source', 'add', '-n', notebook_id, source, '--json')['source']

    def wait_source(self, notebook_id: str, source_id: str, timeout: int = 300) -> dict:
        return self._run_json('source', 'wait', '-n', notebook_id, source_id, '--timeout', str(timeout), '--json')

    def generate_report(self, notebook_id: str, report_append: str) -> dict:
        return self._run_json('generate', 'report', '-n', notebook_id, '--format', 'study-guide', '--append', report_append, '--json')

    def wait_artifact(self, notebook_id: str, artifact_id: str, timeout: int = 900) -> dict:
        return self._run_json('artifact', 'wait', '-n', notebook_id, artifact_id, '--timeout', str(timeout), '--json')

    def generate_mind_map(self, notebook_id: str) -> dict:
        return self._run_json('generate', 'mind-map', '-n', notebook_id, '--json')

    def ask(self, notebook_id: str, question: str) -> dict:
        return self._run_json('ask', '-n', notebook_id, question, '--json')

    def download_report(self, notebook_id: str, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self._run('download', 'report', '-n', notebook_id, str(output_path), '--force')

    def download_mind_map(self, notebook_id: str, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self._run('download', 'mind-map', '-n', notebook_id, str(output_path), '--force')


def run_qmd_update(command: str = 'qmd') -> str:
    result = subprocess.run([command, 'update'], check=True, text=True, capture_output=True)
    return result.stdout.strip()
