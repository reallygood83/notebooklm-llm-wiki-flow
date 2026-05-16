"""AURA Content Router.

Classifies and routes Markdown files to the correct PARA+ folders.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from google import genai

from .common import get_logger, step

LOG = get_logger("ax.route")

def classify_content(content: str) -> str:
    """Classify content into WORK, PERSONA, or RESOURCE using Gemini."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        LOG.error("GEMINI_API_KEY not found.")
        return "RESOURCE"

    client = genai.Client(api_key=api_key)

    prompt = f"""
Analyze the nature of the following text and classify it into one of the 3 categories:
- WORK: Administrative, planning, reports, IT development, work-related documents.
- PERSONA: Essays, diaries, personal thoughts, family, philosophy, personal writings.
- RESOURCE: Information scraps, news, simple references not fitting the above.

Output exactly one word in uppercase: WORK, PERSONA, or RESOURCE.

Text:
{content[:2000]}
"""
    try:
        response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        category = (response.text or "").strip().upper()
        if "WORK" in category: return "WORK"
        if "PERSONA" in category: return "PERSONA"
        return "RESOURCE"
    except Exception as e:
        LOG.error(f"Gemini classification failed: {e}")
        return "RESOURCE"

def route_file(file_path: Path, vault_dir: Path) -> Path | None:
    """Routes a file based on its content classification."""
    if not file_path.is_file():
        return None
        
    with step(LOG, f"route-{file_path.name}"):
        content = file_path.read_text(encoding="utf-8")
        category = classify_content(content)
        
        target_map = {
            "WORK": vault_dir / "work" / "02_Incoming_Raw",
            "PERSONA": vault_dir / "persona" / "02_Incoming_Raw",
            "RESOURCE": vault_dir / "resource"
        }
        
        target_dir = target_map.get(category, vault_dir / "resource")
        target_dir.mkdir(parents=True, exist_ok=True)
        
        dest_path = target_dir / file_path.name
        shutil.move(str(file_path), str(dest_path))
        
        LOG.info(f"Routed: {file_path.name} -> {category}")
        return dest_path
