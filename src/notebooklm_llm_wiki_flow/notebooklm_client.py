from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol, runtime_checkable

JSONDict = dict[str, Any]


class NotebookLMError(Exception):
    """Base exception for NotebookLM client failures."""


class NotebookLMCommandError(NotebookLMError):
    def __init__(self, *, step: str, command: list[str], stderr: str = "", stdout: str = "", returncode: int | None = None) -> None:
        self.step = step
        self.command = command
        self.stderr = stderr
        self.stdout = stdout
        self.returncode = returncode
        message = f"NotebookLM command failed during {step}: {' '.join(command)}"
        if stderr:
            message = f"{message} | stderr: {stderr}"
        elif stdout:
            message = f"{message} | stdout: {stdout}"
        super().__init__(message)


class NotebookLMTimeoutError(NotebookLMError):
    def __init__(self, *, step: str, command: list[str], timeout_seconds: int | None = None) -> None:
        self.step = step
        self.command = command
        self.timeout_seconds = timeout_seconds
        message = f"NotebookLM command timed out during {step}: {' '.join(command)}"
        if timeout_seconds is not None:
            message = f"{message} after {timeout_seconds}s"
        super().__init__(message)


@runtime_checkable
class NotebookLMClient(Protocol):
    def create_notebook(self, title: str) -> JSONDict: ...
    def add_source(self, notebook_id: str, source: str) -> JSONDict: ...
    def wait_source(self, notebook_id: str, source_id: str, timeout: int = 300) -> JSONDict: ...
    def generate_report(self, notebook_id: str, report_append: str) -> JSONDict: ...
    def wait_artifact(self, notebook_id: str, artifact_id: str, timeout: int = 900) -> JSONDict: ...
    def generate_mind_map(self, notebook_id: str) -> JSONDict: ...
    def ask(self, notebook_id: str, question: str) -> JSONDict: ...
    def download_report(self, notebook_id: str, output_path: Path) -> None: ...
    def download_mind_map(self, notebook_id: str, output_path: Path) -> None: ...
