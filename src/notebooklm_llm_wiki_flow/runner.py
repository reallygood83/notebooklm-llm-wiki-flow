from __future__ import annotations

import json
import logging
import subprocess
import time
from pathlib import Path

from .notebooklm_client import JSONDict, NotebookLMCommandError, NotebookLMTimeoutError

logger = logging.getLogger(__name__)


class NotebookLMRunner:
    def __init__(
        self,
        command: str = 'notebooklm',
        *,
        max_retries: int = 0,
        retry_backoff_seconds: float = 1.0,
    ) -> None:
        if max_retries < 0:
            raise ValueError("max_retries must be >= 0")
        self.command = command
        self.max_retries = max_retries
        self.retry_backoff_seconds = retry_backoff_seconds

    def _command(self, *args: str) -> list[str]:
        return [self.command, *args]

    def _run(self, step: str, *args: str, timeout_seconds: int | None = None) -> str:
        command = self._command(*args)
        attempts = self.max_retries + 1
        last_error: Exception | None = None
        for attempt in range(1, attempts + 1):
            try:
                result = subprocess.run(
                    command,
                    check=True,
                    text=True,
                    capture_output=True,
                    timeout=timeout_seconds,
                )
                return result.stdout.strip()
            except subprocess.CalledProcessError as exc:
                last_error = NotebookLMCommandError(
                    step=step,
                    command=list(exc.cmd) if isinstance(exc.cmd, (list, tuple)) else command,
                    stderr=(exc.stderr or '').strip(),
                    stdout=(exc.stdout or '').strip(),
                    returncode=exc.returncode,
                )
            except subprocess.TimeoutExpired as exc:
                last_error = NotebookLMTimeoutError(
                    step=step,
                    command=list(exc.cmd) if isinstance(exc.cmd, (list, tuple)) else command,
                    timeout_seconds=int(exc.timeout) if exc.timeout is not None else None,
                )
            if attempt < attempts:
                logger.warning(
                    "notebooklm step '%s' failed on attempt %d/%d; retrying in %.1fs",
                    step,
                    attempt,
                    attempts,
                    self.retry_backoff_seconds,
                )
                time.sleep(self.retry_backoff_seconds)
        assert last_error is not None
        raise last_error

    def _run_json(self, step: str, *args: str, timeout_seconds: int | None = None) -> JSONDict:
        command = self._command(*args)
        stdout = self._run(step, *args, timeout_seconds=timeout_seconds)
        try:
            payload = json.loads(stdout)
        except json.JSONDecodeError as exc:
            raise NotebookLMCommandError(
                step=step,
                command=command,
                stdout=stdout,
            ) from exc
        if not isinstance(payload, dict):
            raise NotebookLMCommandError(
                step=step,
                command=command,
                stdout=stdout,
            )
        return payload

    def _run_json_field(self, step: str, field: str, *args: str, timeout_seconds: int | None = None) -> JSONDict:
        payload = self._run_json(step, *args, timeout_seconds=timeout_seconds)
        try:
            value = payload[field]
        except KeyError as exc:
            raise NotebookLMCommandError(
                step=step,
                command=self._command(*args),
                stdout=json.dumps(payload, ensure_ascii=False),
            ) from exc
        if not isinstance(value, dict):
            raise NotebookLMCommandError(
                step=step,
                command=self._command(*args),
                stdout=json.dumps(payload, ensure_ascii=False),
            )
        return value

    def create_notebook(self, title: str) -> JSONDict:
        return self._run_json_field('create_notebook', 'notebook', 'create', title, '--json')

    def add_source(self, notebook_id: str, source: str) -> JSONDict:
        return self._run_json_field('add_source', 'source', 'source', 'add', '-n', notebook_id, source, '--json')

    def wait_source(self, notebook_id: str, source_id: str, timeout: int = 300) -> JSONDict:
        return self._run_json(
            'wait_source',
            'source',
            'wait',
            '-n',
            notebook_id,
            source_id,
            '--timeout',
            str(timeout),
            '--json',
            timeout_seconds=timeout + 5,
        )

    def generate_report(self, notebook_id: str, report_append: str) -> JSONDict:
        return self._run_json('generate_report', 'generate', 'report', '-n', notebook_id, '--format', 'study-guide', '--append', report_append, '--json')

    def wait_artifact(self, notebook_id: str, artifact_id: str, timeout: int = 900) -> JSONDict:
        return self._run_json(
            'wait_artifact',
            'artifact',
            'wait',
            '-n',
            notebook_id,
            artifact_id,
            '--timeout',
            str(timeout),
            '--json',
            timeout_seconds=timeout + 5,
        )

    def generate_mind_map(self, notebook_id: str) -> JSONDict:
        return self._run_json('generate_mind_map', 'generate', 'mind-map', '-n', notebook_id, '--json')

    def ask(self, notebook_id: str, question: str) -> JSONDict:
        return self._run_json('ask', 'ask', '-n', notebook_id, question, '--json')

    def download_report(self, notebook_id: str, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self._run('download_report', 'download', 'report', '-n', notebook_id, str(output_path), '--force')

    def download_mind_map(self, notebook_id: str, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self._run('download_mind_map', 'download', 'mind-map', '-n', notebook_id, str(output_path), '--force')


def run_qmd_update(command: str = 'qmd') -> str:
    result = subprocess.run([command, 'update'], check=True, text=True, capture_output=True)
    return result.stdout.strip()
