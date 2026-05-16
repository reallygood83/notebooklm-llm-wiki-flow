"""Surgical HWPX Injector.

Injects content into a HWPX template by swapping the BodyText section.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import cast

from .common import escape_xml_text, get_logger, read_hwpx, step, write_hwpx_from_entries

LOG = get_logger("ax.hwpx")

# Matches the contents of hp:section (BodyText). 매치된 네임스페이스 prefix(hp/hs)를 명시
# 캡처해 본문 생성 시에도 동일 ns를 쓰도록 한다.
SECTION_RE = re.compile(
    r"(<(?P<ns>hp|hs):section[^>]*>)(.*?)(</(?P=ns):section>)",
    re.DOTALL,
)


def md_to_hwpx_xml_fragment(md_text: str, ns: str = "hp") -> str:
    """Markdown을 HWPX XML fragment(<ns>:p, <ns>:run)로 변환. ns는 'hp' 또는 'hs'."""
    lines = md_text.splitlines()
    xml_lines = []

    for line in lines:
        line = line.strip()
        if not line:
            xml_lines.append(f"<{ns}:p><{ns}:run><{ns}:t/></{ns}:run></{ns}:p>")
            continue

        escaped = escape_xml_text(line)
        xml_lines.append(
            f"<{ns}:p><{ns}:run><{ns}:t>{escaped}</{ns}:t></{ns}:run></{ns}:p>"
        )

    return "\n".join(xml_lines)

def inject_md_into_hwpx(md_path: Path, template_path: Path, output_path: Path) -> Path:
    """Injects Markdown content into a HWPX template."""
    with step(LOG, "read-files"):
        md_text = md_path.read_text(encoding="utf-8")
        entries = read_hwpx(str(template_path))
        
    with step(LOG, "transform-content"):
        # 1. Find section0.xml (usually the first section)
        section_key = "Contents/section0.xml"
        if section_key not in entries:
            for k in entries.keys():
                if k.startswith("Contents/section") and k.endswith(".xml"):
                    section_key = k
                    break
            else:
                raise KeyError("Could not find any section XML in template")

        xml_content = entries[section_key].decode("utf-8")

        # 2. 매치된 네임스페이스를 먼저 확인하여 동일 ns로 본문 생성
        first_match = SECTION_RE.search(xml_content)
        if first_match is None:
            raise ValueError(
                f"HWPX injection failed: <hp|hs:section> tag not found in {section_key}. "
                "Template structure not supported; aborting to avoid silent content loss."
            )
        ns = first_match.group("ns")
        new_content = md_to_hwpx_xml_fragment(md_text, ns=ns)

        # 3. Surgical Swap (네임스페이스 일관성 확보 후 안전한 치환)
        def _swap(match: "re.Match[str]") -> str:
            prefix = match.group(1)
            suffix = match.group(4)
            return f"{prefix}{new_content}{suffix}"

        # count=1 — 다중 섹션이 있는 템플릿에서 모든 section을 동일 본문으로 덮어쓰지
        # 않도록 첫 매치만 치환. (bug_033)
        updated_xml, count = SECTION_RE.subn(_swap, xml_content, count=1)
        if count == 0:
            # first_match이 있었으니 도달 불가하지만 방어적으로 raise
            raise RuntimeError(
                "HWPX section swap produced 0 replacements despite earlier match."
            )

        entries[section_key] = updated_xml.encode("utf-8")
        
    with step(LOG, "package-hwpx"):
        write_hwpx_from_entries(cast("dict[str, bytes | str]", entries), str(output_path))
        
    return output_path
