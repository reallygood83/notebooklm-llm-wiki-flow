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
    """Classify content into WORK, PERSONA, or RESOURCE using Gemini.

    Key 부재나 API 실패는 'RESOURCE'로 무음 폴백하지 않고 예외를 발생시킨다.
    잘못된 분류로 사용자 파일이 의도와 다른 폴더로 이동하는 것을 방지하기 위함.

    표준 변수명은 ``GOOGLE_API_KEY``(google-genai SDK 및 nlwflow-repo .env와 일치).
    ``GEMINI_API_KEY``도 하위 호환으로 수용한다.
    """
    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GOOGLE_API_KEY (또는 GEMINI_API_KEY) environment variable is required "
            "for classification. Set it before running `nlwflow ax route` to avoid "
            "silent misclassification."
        )

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
        response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    except Exception as e:
        raise RuntimeError(f"Gemini classification API call failed: {e}") from e

    # exact match로 첫 토큰만 검사. `in` 부분일치는 'WORKFLOW'·'PERSONAL'·'OUTSOURCES'
    # 같은 응답이 잘못 매칭되어 오라우팅을 일으킨다.
    raw = (response.text or "").strip().upper()
    first_token = raw.split()[0] if raw.split() else ""
    if first_token in {"WORK", "PERSONA", "RESOURCE"}:
        return first_token
    raise ValueError(
        f"Gemini returned unexpected category: {raw!r}. "
        "Expected one of WORK / PERSONA / RESOURCE."
    )


def route_file(file_path: Path, vault_dir: Path) -> Path:
    """Routes a file based on its content classification. 실패 시 raise."""
    if not file_path.is_file():
        raise FileNotFoundError(f"Source file not found or not a regular file: {file_path}")

    with step(LOG, f"route-{file_path.name}"):
        content = file_path.read_text(encoding="utf-8")
        category = classify_content(content)

        target_map = {
            "WORK": vault_dir / "work" / "02_Incoming_Raw",
            "PERSONA": vault_dir / "persona" / "02_Incoming_Raw",
            "RESOURCE": vault_dir / "resource",
        }
        target_dir = target_map[category]
        target_dir.mkdir(parents=True, exist_ok=True)

        dest_path = target_dir / file_path.name
        if dest_path.exists():
            raise FileExistsError(
                f"Destination already exists: {dest_path}. Aborting route to prevent "
                "overwriting existing content (silent data loss)."
            )
        shutil.move(str(file_path), str(dest_path))

        LOG.info(f"Routed: {file_path.name} -> {category}")
        return dest_path
