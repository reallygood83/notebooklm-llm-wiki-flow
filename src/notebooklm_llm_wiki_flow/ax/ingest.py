"""AURA Ingestion Tool.

Converts documents (HWPX, HWP, PDF, DOCX, XLSX) to Markdown via kordoc.
실패·누락 시 silent None 대신 명시적 예외를 발생시켜 호출자가 인지할 수 있게 한다.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from .common import get_logger, step

LOG = get_logger("ax.ingest")

SUPPORTED_EXTENSIONS = (".hwpx", ".hwp", ".pdf", ".docx", ".xlsx")


def _resolve_npx() -> str:
    """PATH에서 npx 실행 파일을 동적 탐색. Apple Silicon·Linux·CI 호환."""
    npx_path = shutil.which("npx")
    if not npx_path:
        raise FileNotFoundError(
            "npx not found on PATH. Install Node.js (e.g. Homebrew `brew install node`) "
            "or ensure /opt/homebrew/bin or /usr/local/bin is on PATH."
        )
    return npx_path


def ingest_file(input_path: Path, output_dir: Path) -> Path:
    """Ingest a single file via kordoc. 실패 시 raise (silent None 반환 금지)."""
    if input_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported extension: {input_path.suffix!r}. "
            f"Supported: {', '.join(SUPPORTED_EXTENSIONS)}"
        )

    npx = _resolve_npx()
    with step(LOG, f"ingest-{input_path.name}"):
        try:
            subprocess.run(
                [npx, "kordoc", str(input_path), "-d", str(output_dir)],
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"kordoc conversion failed for {input_path.name}: "
                f"rc={e.returncode}, stderr={e.stderr.strip()}"
            ) from e

        output_file = output_dir / (input_path.stem + ".md")
        if not output_file.exists():
            raise FileNotFoundError(
                f"kordoc ran successfully but expected output not found: {output_file}"
            )

        content = output_file.read_text(encoding="utf-8")
        output_file.write_text(
            f"--- [AI_COMPACTION_REQUIRED] ---\n\n{content}", encoding="utf-8"
        )
        return output_file
