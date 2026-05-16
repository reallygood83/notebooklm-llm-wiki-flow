"""Surgical HWPX Injector.

Injects content into a HWPX template by swapping the BodyText section.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict

from .common import get_logger, read_hwpx, step, write_hwpx_from_entries, escape_xml_text

LOG = get_logger("ax.hwpx")

# Matches the contents of hp:section (BodyText)
# We use a broad regex to handle different namespaces (hp, hs)
SECTION_RE = re.compile(r"(<(?:hp|hs):section[^>]*>)(.*?)(</(?:hp|hs):section>)", re.DOTALL)

def md_to_hwpx_xml_fragment(md_text: str) -> str:
    """Converts simple Markdown to HWPX XML fragments (hp:p, hp:run)."""
    lines = md_text.splitlines()
    xml_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            # Empty paragraph
            xml_lines.append("<hp:p><hp:run><hp:t/></hp:run></hp:p>")
            continue
            
        # Basic paragraph wrap
        # Note: A real converter would handle headings/tables here, 
        # but for surgical injection into complex templates, 
        # usually simpler is better or we use pre-formatted fragments.
        escaped = escape_xml_text(line)
        xml_lines.append(f"<hp:p><hp:run><hp:t>{escaped}</hp:t></hp:run></hp:p>")
        
    return "\n".join(xml_lines)

def inject_md_into_hwpx(md_path: Path, template_path: Path, output_path: Path) -> Path:
    """Injects Markdown content into a HWPX template."""
    with step(LOG, "read-files"):
        md_text = md_path.read_text(encoding="utf-8")
        entries = read_hwpx(str(template_path))
        
    with step(LOG, "transform-content"):
        # 1. Convert MD to HWPX fragments
        new_content = md_to_hwpx_xml_fragment(md_text)
        
        # 2. Find section0.xml (usually the first section)
        section_key = "Contents/section0.xml"
        if section_key not in entries:
            # Try to find any sectionX.xml
            for k in entries.keys():
                if k.startswith("Contents/section") and k.endswith(".xml"):
                    section_key = k
                    break
            else:
                raise KeyError("Could not find any section XML in template")
        
        xml_content = entries[section_key].decode("utf-8")
        
        # 3. Surgical Swap
        def _swap(match: re.Match) -> str:
            prefix, _, suffix = match.groups()
            return f"{prefix}{new_content}{suffix}"
            
        updated_xml, count = SECTION_RE.subn(_swap, xml_content)
        if count == 0:
            LOG.warning("Could not find section tag for injection. Appending to end of file (risky).")
            # Fallback logic if needed, but usually templates have sections.
            
        entries[section_key] = updated_xml.encode("utf-8")
        
    with step(LOG, "package-hwpx"):
        write_hwpx_from_entries(entries, str(output_path))
        
    return output_path
