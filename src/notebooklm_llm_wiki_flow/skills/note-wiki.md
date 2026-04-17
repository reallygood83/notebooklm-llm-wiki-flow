---
description: NotebookLM 으로 리서치하고 그 결과를 LLM Wiki 구조로 Obsidian vault 에 저장합니다.
argument-hint: <research prompt with URLs or topic>
---

사용자가 `/note-wiki` 뒤에 입력한 프롬프트: **$ARGUMENTS**

너는 `nlwflow note-wiki` CLI 를 실행해서 NotebookLM → LLM Wiki → Obsidian 파이프라인을 구동해야 한다.

## 실행 절차

### 1. nlwflow CLI 위치 확인
다음 순서로 `nlwflow` 실행 파일을 찾는다.
1. 현재 작업 디렉터리의 `./.venv/bin/nlwflow`
2. `$PATH` 의 `nlwflow` (Bash 로 `command -v nlwflow` 확인)
3. 둘 다 없으면 사용자에게 `./scripts/bootstrap.sh` 실행을 안내하고 종료.

### 2. 프롬프트에서 source URL 감지
`$ARGUMENTS` 안에 `http://` / `https://` 로 시작하는 URL 이 하나 이상 있어야 한다.
없으면 사용자에게 **최소 1개의 source URL** 을 요청한다. (NotebookLM 이 자료를 읽으려면 URL 이 필요)

### 3. dry-run 으로 플랜 확인 (권장)
먼저 다음 명령으로 계획만 출력해 사용자에게 확인받는다.

```bash
./.venv/bin/nlwflow note-wiki "$ARGUMENTS" --dry-run --json
```

출력된 JSON 에서 `plan.title`, `plan.sources`, `plan.wiki_outputs` 를 요약해 보여준다.

### 4. 실제 실행
사용자가 승인하면 `--dry-run` 없이 실행한다.

```bash
./.venv/bin/nlwflow note-wiki "$ARGUMENTS" --json
```

옵션이 필요하면 추가로 덧붙인다.
- `--source <URL>` 원문 URL 을 프롬프트 밖에서 추가할 때
- `--title "<title>"` 생성될 comparison 페이지 제목
- `--vault <path>` Obsidian vault 경로 override
- `--wiki-path <path>` LLM Wiki 루트 override
- `--no-qmd-update` qmd 인덱스 갱신 스킵

### 5. 결과 보고
JSON payload 에서 다음을 뽑아 사용자에게 요약한다.
- `notebook_id` — NotebookLM 노트북 ID
- `comparison_page` — 생성된 비교 페이지 경로 (Obsidian 에서 열 수 있음)
- `inbox_note` — Inbox 에 떨어진 note
- `manifest_path` — 이번 실행의 audit manifest (`artifacts/<id>/manifest.json`)
- `resolved_config.obsidian_vault`, `resolved_config.wiki_path`

각 파일 경로는 `file_path:line_number` 형태가 아닌 절대경로로 표시한다.

### 6. (선택) 열기 제안
`comparison_page` 또는 `inbox_note` 를 `open` (macOS) / 기본 에디터로 열 수 있는지 사용자에게 묻는다.

## 주의사항
- NotebookLM 브라우저 로그인이 안 된 상태라면 실행 전에 `./.venv/bin/notebooklm login` 을 먼저 실행하도록 안내한다.
- 실행은 수 분이 걸릴 수 있다 (NotebookLM 이 source 를 ingest 하는 시간).
- LLM Wiki 는 6대 우선순위 규칙을 강제한다 — obligations / retention / minor safety / human review / enterprise controls / legal risk.
  따라서 marketing copy 같은 generic 콘텐츠는 의도적으로 제외된다. 이게 정상 동작임을 사용자에게 설명한다.
