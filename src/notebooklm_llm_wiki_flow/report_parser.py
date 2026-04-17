from __future__ import annotations

import re

from .models import ReportHighlights, ReportSection

PRIORITY_KEYWORDS = {
    "policy", "privacy", "retention", "training", "ownership", "education",
    "student", "minor", "academic", "integrity", "human review", "compliance",
    "data", "security", "admin", "checklist", "risk",
}

SECTION_RE = re.compile(r'^##+\s+(.*)$', re.M)


def _score(title: str, body: str) -> int:
    haystack = f"{title} {body}".lower()
    score = sum(3 for keyword in PRIORITY_KEYWORDS if keyword in haystack)
    score += len(re.findall(r'\d+', haystack))
    return score


def extract_report_highlights(markdown: str, max_sections: int = 4, max_bullets: int = 8) -> ReportHighlights:
    title_match = re.search(r'^#\s+(.*)$', markdown, re.M)
    title = title_match.group(1).strip() if title_match else 'NotebookLM report'

    sections: list[ReportSection] = []
    matches = list(SECTION_RE.finditer(markdown))
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        section_title = re.sub(r'^\d+[.)]\s*', '', match.group(1).strip())
        body = markdown[start:end].strip()
        sections.append(ReportSection(title=section_title, body=body, score=_score(section_title, body)))

    sections.sort(key=lambda item: item.score, reverse=True)
    selected = sections[:max_sections]

    bullets: list[str] = []
    for section in selected:
        for raw_line in section.body.splitlines():
            line = raw_line.strip().lstrip('*').lstrip('-').strip()
            if not line:
                continue
            if len(line) < 12:
                continue
            if line not in bullets:
                bullets.append(line)
            if len(bullets) >= max_bullets:
                break
        if len(bullets) >= max_bullets:
            break

    return ReportHighlights(title=title, sections=selected, bullets=bullets)
