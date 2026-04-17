from __future__ import annotations

from pathlib import Path


KIT_FILES = {
    Path('000-Inbox/NLW Getting Started.md'): """---
title: NLW Getting Started
tags: [notebooklm, llm-wiki, obsidian]
---

# NLW Getting Started

이 Vault는 notebooklm-llm-wiki-flow와 함께 사용하도록 준비되었습니다.

## 핵심 규칙
- properties에 source_urls를 넣어 클릭으로 원문 이동
- comparison/query/entity 페이지는 source_notes와 source_urls를 함께 유지
- high-signal policy claims를 우선 보존
""",
    Path('100-Templates/NLW Comparison Template.md'): """---
title: 
created: 
updated: 
type: comparison
tags: []
source_notes: []
source_urls: []
---

# 

## Side-by-side comparison

## Checklist

## Related
""",
    Path('100-Templates/NLW Query Template.md'): """---
title: 
created: 
updated: 
type: query
tags: []
source_notes: []
source_urls: []
---

# 

## Prompt

## Answer
""",
    Path('900-System/nlwflow-obsidian-skills-guide.md'): """---
title: nlwflow Obsidian skills guide
---

# nlwflow Obsidian skills guide

이 저장소는 Hermes의 obsidian skill 스타일을 따르도록 설계되었습니다.

## Property rules
- `source_notes`: vault 내부 raw note 또는 wiki note 링크용
- `source_urls`: 외부 원문 URL용, Obsidian properties에서 클릭 가능
- `share_link`: ShareNote 사용 시 자동 업데이트 가능

obsidian skills가 없는 사용자도 이 starter kit만 복사하면 동일한 note 구조를 사용할 수 있습니다.
""",
}


def install_obsidian_kit(vault_path: str | Path) -> list[str]:
    root = Path(vault_path).expanduser().resolve()
    created: list[str] = []
    for rel_path, content in KIT_FILES.items():
        target = root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            target.write_text(content, encoding='utf-8')
            created.append(str(target))
    return created
