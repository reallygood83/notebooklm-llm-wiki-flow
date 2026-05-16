---
description: NotebookLM 으로 리서치하고 그 결과를 LLM Wiki 구조로 Obsidian vault 에 저장합니다.
argument-hint: <research prompt with URLs or topic>
---

# [Command] note-wiki

사용자가 `/note-wiki` 뒤에 입력한 프롬프트: **$ARGUMENTS**

너는 `nlwflow note-wiki` CLI 를 실행해서 NotebookLM → LLM Wiki → Obsidian 파이프라인을 구동해야 한다.

---

## 실행 절차

### 0. 지침 문서 로드 (필수 — 실행 전 반드시 먼저 수행)

아래 두 파일을 읽어서 이번 작업의 품질 기준으로 삼는다.
이 파일들의 내용은 실행 후 결과를 평가하고 보고할 때 반드시 적용한다.

1. **콘텐츠 품질 기준**: `config/prompts/llm_wiki_priority.md`
   - 어떤 정보를 보존하고 어떤 정보를 버릴지 판단하는 우선순위 기준
   - 결과물 품질 체크리스트 포함

2. **비교 분석 기준**: `config/prompts/policy_compare.md`
   - 두 개 이상의 문서·정책을 비교할 때 반드시 확인할 항목
   - 생성해야 할 산출물 목록 포함

두 파일을 읽은 후, 이번 작업에서 적용할 기준을 내부적으로 확인하고 실행을 계속한다.

---

### 1. 도메인 판별 (work / persona)

사용자의 프롬프트를 읽고, 결과물이 **업무(work)**용인지 **개인(persona)**용인지 판별한다.

- 업무·행정·법률·정책·기술 분석 → **work**
- 에세이·감성·개인 기록·글감 → **persona**

**판별이 불확실한 경우**, 사용자에게 반드시 먼저 묻는다.
> "이 리서치 결과를 업무(work) 영역에 저장할까요, 개인(persona) 영역에 저장할까요?"

---

### 2. nlwflow CLI 위치 확인

다음 순서로 `nlwflow` 실행 파일을 찾는다.

1. 현재 작업 디렉터리의 `./.venv/bin/nlwflow`
2. `$PATH` 의 `nlwflow` (Bash 로 `command -v nlwflow` 확인)
3. 둘 다 없으면 사용자에게 `./scripts/bootstrap.sh` 실행을 안내하고 종료.

---

### 3. 프롬프트에서 source URL 감지

`$ARGUMENTS` 안에 `http://` / `https://` 로 시작하는 URL 이 하나 이상 있어야 한다.
없으면 사용자에게 **최소 1개의 source URL** 을 요청한다. (NotebookLM 이 자료를 읽으려면 URL 이 필요)

---

### 4. dry-run 으로 플랜 확인 (권장)

먼저 다음 명령으로 계획만 출력해 사용자에게 확인받는다.

```bash
./.venv/bin/nlwflow note-wiki "$ARGUMENTS" --dry-run --json
```

출력된 JSON 에서 `plan.title`, `plan.sources`, `plan.wiki_outputs` 를 요약해 보여준다.

---

### 5. 실제 실행

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

---

### 6. 결과물 라우팅 (Obsidian 저장 위치)

실행이 완료되면, 생성된 결과물을 **도메인(work/persona)에 맞는 폴더**로 배치한다.
Obsidian Vault 루트: `/Users/choichanghoon/Obsidian Vault/My Vault/`

#### work 도메인인 경우

| 산출물 유형 | 저장 위치 | 이유 |
| --- | --- | --- |
| 비교 분석 페이지 (Comparison) | `work/03_Refined/` | 이미 AI가 정제한 분석 결과물 |
| 실행 체크리스트 (Checklist) | `work/03_Refined/` | 즉시 활용 가능한 업무 자산 |
| 원문 출처 보존 (Raw Source) | `work/02_Incoming_Raw/` | 유일하게 '날것'에 해당하는 자료 |
| 핵심 용어·엔티티 (Entity) | `work/04_Dictionary/` | 기존 사전 체계에 자연스럽게 편입 |

#### persona 도메인인 경우

| 산출물 유형 | 저장 위치 | 이유 |
| --- | --- | --- |
| 비교 분석 페이지 (Comparison) | `persona/03_Refined/` | 정제된 분석 결과물 |
| 실행 체크리스트 (Checklist) | `persona/03_Refined/` | 활용 가능한 개인 자산 |
| 원문 출처 보존 (Raw Source) | `persona/02_Incoming_Raw/` | 날것 자료 보존 |
| 핵심 용어·엔티티 (Entity) | `persona/04_Dictionary/` | 개인 사전 체계에 편입 |

#### 저장 시 필수 사항

- 모든 파일에 YAML Frontmatter(문서 머리말 속성)를 포함한다: `title`, `created`, `updated`, `tags`, `source_urls`
- 정제 문서 하단에 "참조 원문: `[[파일명]]`" 형식으로 Raw Source와 백링크를 연결한다.
- `04_Dictionary`에 등록하는 용어는 **짧은 정의 문서(200자 이내 개요)** 형식을 유지한다.

---

### 7. 결과 품질 검증 (필수 — 보고 전에 수행)

실행이 완료되면, 0단계에서 읽은 `llm_wiki_priority.md` 의 **결과물 품질 체크리스트**를 기준으로 결과를 평가한다.

아래 항목을 확인하고, 미충족 항목이 있으면 사용자에게 명시적으로 보고한다.

- [ ] 비교 페이지(Comparison)가 생성되었는가?
- [ ] 실행 가능한 체크리스트(Checklist)가 포함되었는가?
- [ ] 원문 출처(Raw Source)가 provenance와 함께 저장되었는가?
- [ ] 생성된 콘텐츠가 "의사결정에 즉시 활용 가능한" 수준인가?
- [ ] 마케팅성 내용이 핵심 내용을 가리지 않았는가?
- [ ] 결과물이 올바른 도메인(work/persona)의 올바른 폴더에 배치되었는가?

---

### 8. 결과 보고

JSON payload 에서 다음을 뽑아 사용자에게 요약한다.

- `notebook_id` — NotebookLM 노트북 ID
- **저장된 파일 목록** — 각 파일의 절대경로와 배치된 폴더
- `manifest_path` — 이번 실행의 audit manifest (`artifacts/<id>/manifest.json`)

**품질 검증 결과를 함께 보고한다.** 체크리스트에서 미충족 항목이 있으면 "⚠️ 확인 필요" 로 표시한다.

---

### 9. (선택) 열기 제안

비교 분석 페이지 또는 체크리스트를 `open` (macOS) / 기본 에디터로 열 수 있는지 사용자에게 묻는다.

---

## 주의사항

- NotebookLM 브라우저 로그인이 안 된 상태라면 실행 전에 `./.venv/bin/notebooklm login` 을 먼저 실행하도록 안내한다.
- 실행은 수 분이 걸릴 수 있다 (NotebookLM 이 source 를 ingest 하는 시간).
- `llm_wiki_priority.md` 의 우선순위 기준에 따라, 마케팅성 콘텐츠와 퀴즈·용어 해설은 의도적으로 제외된다. 이것이 정상 동작임을 사용자에게 설명한다.
- 이 체계는 GIST AX 혁신 업무의 지식 자산화를 목적으로 운영된다. 모든 결과물은 실제 행정 판단에 활용 가능한 수준이어야 한다.
