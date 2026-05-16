"""AURA Ingestion Tool.

Converts documents (HWPX, HWP, PDF, DOCX, XLSX) to Markdown.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from .common import get_logger, step

LOG = get_logger("ax.ingest")

SUPPORTED_EXTENSIONS = ('.hwpx', '.hwp', '.pdf', '.docx', '.xlsx')

def ingest_file(input_path: Path, output_dir: Path) -> Path | None:
    """Ingests a single file using the kordoc engine."""
    if input_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        LOG.warning(f"Unsupported extension: {input_path.suffix}")
        return None

    with step(LOG, f"ingest-{input_path.name}"):
        # Use npx kordoc as the primary conversion engine
        try:
            # Prepare environment for Node.js
            env = os.environ.copy()
            env["PATH"] = "/usr/local/bin:" + env.get("PATH", "")
            
            subprocess.run(
                ['/usr/local/bin/npx', 'kordoc', str(input_path), '-d', str(output_dir)],
                capture_output=True, text=True, env=env, check=True
            )
            
            # Find the output file (usually same name but .md)
            output_file = output_dir / (input_path.stem + ".md")
            if output_file.exists():
                # Add compaction trigger as per AURA standards
                content = output_file.read_text(encoding="utf-8")
                output_file.write_text(f"--- [AI_COMPACTION_REQUIRED] ---\n\n{content}", encoding="utf-8")
                return output_file
                
        except subprocess.CalledProcessError as e:
            LOG.error(f"Kordoc failed: {e.stderr}")
            return None
        except Exception as e:
            LOG.error(f"Ingestion error: {e}")
            return None
            
    return None
