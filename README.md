# notebooklm-llm-wiki-flow

[![CI](https://github.com/reallygood83/notebooklm-llm-wiki-flow/actions/workflows/ci.yml/badge.svg)](https://github.com/reallygood83/notebooklm-llm-wiki-flow/actions)

NotebookLM 출력물을 **LLM Wiki** 에 축적하고 Obsidian·qmd 로 이어주는 **local-first** Python CLI 프로젝트입니다.
A local-first Python CLI that turns NotebookLM output into a structured **LLM Wiki** inside Obsidian and qmd.

> 이 프로젝트의 중심은 NotebookLM 이 아니라 **LLM Wiki** 입니다.
> NotebookLM 은 재료 수집 단계일 뿐, 실제 지식이 쌓이는 곳은 LLM Wiki 입니다.

---

## 🧠 LLM Wiki 란? / What is the LLM Wiki?

**LLM Wiki** 는 LLM이 생성한 일회성 요약물을 "**decision-relevant knowledge layer**" 로 전환하는 지식 구조입니다.
일반 Obsidian vault 나 "AI 노트 앱" 과 결정적으로 다른 점은 **무엇을 저장할지 명시적으로 통제**한다는 것입니다.

### 🇰🇷 한국어
LLM Wiki 는 "LLM 출력 전부를 덤프" 하지 않습니다. 대신 **의사결정에 쓰이는 정보만** 구조화해 저장합니다.

**4종 페이지 타입으로 지식을 분류합니다**:
| 페이지 타입 | 역할 | 저장 위치 |
|-----------|-----|---------|
| **Raw source** | 원문 + provenance (출처·취득일·URL) | `wiki/raw/articles/` |
| **Entity** | 조직·제품·개념 단위 지속 지식 | `wiki/entities/` |
| **Comparison** | side-by-side 비교 문서 | `wiki/comparisons/` |
| **Query / Checklist** | 재사용 가능한 운영 체크리스트 | `wiki/queries/` |

**6대 우선순위 규칙으로 "generic summary dump" 를 방지합니다**:
1. Obligations / prohibitions — 의무·금지 사항
2. Retention numbers / time windows — 보존 기간·숫자 한도
3. Student / minor safety — 학생·미성년자 안전 규칙
4. Human review for high-stakes decisions — 고위험 결정의 사람 검토
5. Enterprise controls — SSO, RBAC, audit log, retention control
6. Ownership / indemnity / legal risk — 소유·면책·법적 위험 배분

즉 LLM Wiki 는 **"무엇을 저장하지 않을지"** 를 먼저 정의한 knowledge layer 입니다. 마케팅 문구, 퀴즈, glossary 같은 generic 텍스트는 의도적으로 배제됩니다.

### 🇬🇧 English
The **LLM Wiki** is a decision-relevant knowledge layer — not a general note dump. It splits ingested material into four page types (`Raw / Entity / Comparison / Query`) and enforces six priority rules (obligations, retention windows, minor safety, human review, enterprise controls, legal risk) so the wiki never degenerates into generic summaries.

Reference:
- `config/prompts/llm_wiki_priority.md` — the 6-rule priority policy
- `docs/llm-wiki-ingestion-standard.md` — the ingestion contract
- `docs/architecture.md` — where LLM Wiki sits in the pipeline

---

## 🔁 파이프라인 / Pipeline

```
NotebookLM              ←  재료 수집 (source gathering)
    ↓
Raw artifacts + parsers ←  report / mind map / Q&A 파싱
    ↓
🧠  LLM Wiki            ←  ★ 이 프로젝트의 핵심 ★
    │                      decision-relevant knowledge layer
    │                      (Raw / Entity / Comparison / Query)
    ↓
Obsidian                ←  human-editable surface
    ↓
qmd                     ←  retrieval / indexing
```

LLM Wiki 가 Obsidian 위가 아니라 **Obsidian 안에서도 분리된 knowledge layer** 라는 점이 핵심입니다. Obsidian 은 편집 UI 를 제공하고, LLM Wiki 는 그 안에서 decision-relevant 구조를 강제합니다.

---

## 왜 이 프로젝트를 쓰는가? / Why use this project?

### 🇰🇷 한국어
NotebookLM 은 강력하지만 결과물이 **일회성 리포트**로 끝나는 한계가 있습니다.
이 프로젝트는 그 결과물을 **LLM Wiki 라는 구조화된 지식 계층**으로 축적하는 local-first 파이프라인입니다.

- NotebookLM 출력을 **LLM Wiki 4종 페이지**로 분류·저장합니다.
- 한 번의 실행으로 comparison / checklist / entity / raw source 가 **동시에** 생성됩니다.
- qmd 인덱싱까지 이어져, 나중에 다시 검색·재사용할 수 있습니다.
- **YAML 기반 재사용 워크플로**로 주제를 계속 확장해도 LLM Wiki 규칙이 일관되게 적용됩니다.

### 🇬🇧 English
NotebookLM is powerful but its output usually ends up as **one-off reports**.
This project is a local-first pipeline that routes those outputs into a **structured LLM Wiki** — the real knowledge layer inside your Obsidian vault.

- Structured, LLM Wiki-aware output instead of disposable notes.
- Generates Comparison, Checklist, Entity, and Raw source pages **in one flow**.
- Closes the loop with qmd indexing so results become searchable and reusable.
- **YAML-based reusable workflows** keep the LLM Wiki rules consistent across new topics.

---

## 사용자가 얻는 실익 / Practical user benefits

NotebookLM + LLM Wiki 를 CLI 파이프라인으로 감싸서 얻는 **구체적 이득**입니다.

### 1. LLM Wiki 가 "지식" 을 남긴다 — Real knowledge retention
- NotebookLM 만 쓰면 **chat·report 가 세션과 함께 사라집니다**.
- LLM Wiki 는 decision-relevant 내용만 **파일로** 남깁니다 — 백링크·태그·검색 모두 동작.
- `## Entities / ## Comparisons / ## Queries` deterministic index 로 쌓이는 지식이 자동 정렬됩니다.

### 2. 토큰/비용 절감 — Token and cost savings
- NotebookLM 이 자체 grounding 을 하므로 Claude/GPT API 로 긴 원문을 재전송할 필요가 없습니다.
- 핵심 파싱은 NotebookLM, 이후는 **deterministic template** 으로 처리해 LLM 호출을 최소화합니다.
- notebook 을 한 번 만들면 이후 대화·재분석은 인증·세션만 유지하면 됩니다.

### 3. 검증 가능한 grounding — Verifiable grounding
- 모든 LLM Wiki 페이지는 `source_notes` + `source_urls` 프론트매터로 **원문과 연결**됩니다.
- Raw source page 는 provenance (취득일·URL·원문 사이트) 를 보존합니다.
- "이 주장 어디서 나왔지?" 라는 질문을 **원문 링크**로 즉시 추적할 수 있습니다.

### 4. "Generic dump" 방지 — Signal over noise
- 6대 우선순위 규칙이 obligations·retention·safety·governance 를 강제 우선합니다.
- 마케팅 문구, glossary, 퀴즈 같은 저신호 콘텐츠가 wiki 를 잠식하지 않도록 설계됨.
- Parser fallback 으로 NotebookLM 비교표가 없어도 bullet 기반 fallback 이 동작합니다.

### 5. 자동화 신뢰성 — Automation reliability
- `NotebookLMClient` Protocol 로 CLI 경계 추상화 — fake client 로 전 과정 테스트 가능.
- `NotebookLMRunner` 는 subprocess 실패를 **typed error + step 컨텍스트**로 감쌈.
- 옵션으로 **retry/backoff** 활성화 가능.

### 6. 안전한 출력 — Safer outputs
- **Staged writes + manifest** — 생성 파일이 staging 을 거쳐 목적지에 반영, 중간 실패 시 반쯤 써진 wiki 상태를 줄임.
- 매 실행마다 `artifacts/<notebook_id>/manifest.json` 이 남아 audit / rollback 이 쉬움.
- Jinja2 `StrictUndefined` 템플릿으로 누락 필드 즉시 감지.

### 7. 협업·재현성·확장성 — Collaboration, reproducibility, scalability
- ruff + mypy (strict) + pytest + **coverage gate 80%** + GitHub Actions (Ubuntu + macOS).
- 환경변수 > `project.yaml` > `.env` > defaults 우선순위 명시적.
- YAML entity rendering 으로 새 주제 확장 시 코드 변경 없이 메타만 수정.

---

## 주요 기능 / Core features

- `nlwflow` Python CLI with Typer + Rich
- **LLM Wiki ingestion standard** (4 page types + 6 priority rules)
- `NotebookLMClient` Protocol + typed runner errors + optional retry
- Typed flow phases (`NotebookRunResult`, `ArtifactExportResult`, `WikiRenderResult`, `PersistResult`, `IndexUpdateResult`)
- Staged writes + SHA256 manifest for each run
- Deterministic LLM Wiki index rebuilder with preamble preservation
- Fake-client integration coverage
- Jinja2-based entity rendering (`StrictUndefined`)
- Parser fallback for non-table NotebookLM reports
- Obsidian starter kit installer
- qmd integration
- GitHub Actions CI matrix (Ubuntu + macOS)

---

## 빠른 시작 / Quick start

### 🇰🇷 한국어
1. 저장소 클론
2. `./scripts/bootstrap.sh` (Python env + notebooklm-py + Playwright + qmd 설치)
3. `notebooklm login` — 브라우저 로그인 1회
4. `./.venv/bin/nlwflow init-config`
5. `./.venv/bin/nlwflow doctor --json`
6. (선택) LLM Wiki + Obsidian starter kit 설치:
   - `./.venv/bin/nlwflow install-obsidian-kit --vault /path/to/vault`
7. 기본 정책 비교 실행:
   - `./.venv/bin/nlwflow run-policy-compare --json`
8. YAML 기반 재사용 워크플로 실행:
   - `./.venv/bin/nlwflow run-from-yaml examples/policy-compare-anthropic-openai-education.yaml --json`

### 🇬🇧 English
1. Clone the repository
2. Run `./scripts/bootstrap.sh`
3. Run `notebooklm login`
4. Run `./.venv/bin/nlwflow init-config`
5. Run `./.venv/bin/nlwflow doctor --json`
6. (Optional) install the LLM Wiki + Obsidian starter kit:
   - `./.venv/bin/nlwflow install-obsidian-kit --vault /path/to/vault`
7. Run the built-in policy comparison:
   - `./.venv/bin/nlwflow run-policy-compare --json`
8. Run a reusable YAML workflow:
   - `./.venv/bin/nlwflow run-from-yaml examples/policy-compare-anthropic-openai-education.yaml --json`

---

## CLI 명령 / CLI commands

| Command | Purpose |
|---------|---------|
| `nlwflow --version` | 버전 출력 |
| `nlwflow doctor` | 환경 점검 (NotebookLM, qmd, LLM Wiki 경로 확인) |
| `nlwflow init-config` | starter config 생성 |
| `nlwflow plan-policy-compare` | 기본 Anthropic vs OpenAI 정책 비교 source pack 출력 |
| `nlwflow run-policy-compare` | NotebookLM notebook 생성 + LLM Wiki 4종 페이지 + index / qmd 갱신 |
| `nlwflow run-from-yaml WORKFLOW.yaml` | YAML 기반 재사용 워크플로 실행 |
| `nlwflow install-obsidian-kit` | LLM Wiki 구조가 포함된 starter vault 설치 |
| `nlwflow score-report REPORT.md` | NotebookLM report 에서 high-signal section 추출 |

---

## 설정 우선순위 / Configuration precedence

1. `NLWFLOW_*` 환경변수
2. `project.yaml`
3. `.env`
4. 내장 기본값

주요 환경변수:
- `NLWFLOW_OBSIDIAN_VAULT` — Obsidian vault 루트
- `NLWFLOW_WIKI_PATH` — LLM Wiki 루트 (vault 안의 하위 경로)
- `NLWFLOW_NOTEBOOKLM_COMMAND`
- `NLWFLOW_QMD_COMMAND`
- `NLWFLOW_QMD_COLLECTION`

---

## LLM Wiki 저장소 구조 / LLM Wiki layout inside the vault

```
<obsidian-vault>/
└── LLM-Wiki/                           ← NLWFLOW_WIKI_PATH
    ├── index.md                        ← deterministic index (## Entities / ## Comparisons / ## Queries)
    ├── log.md                          ← append-only ingest log
    ├── raw/articles/                   ← Raw source pages (with provenance)
    ├── entities/                       ← Entity pages (orgs, products, concepts)
    ├── comparisons/                    ← Comparison pages (side-by-side)
    └── queries/                        ← Query / checklist pages
```

모든 페이지는 `source_notes` + `source_urls` 프론트매터로 **원문과 연결**되며, 6대 우선순위 규칙을 통과한 내용만 저장됩니다.

---

## 프로젝트 구조 / Repository layout

```
src/notebooklm_llm_wiki_flow/   Python package and CLI
  ├── flow.py                   Typed-phase orchestrator (LLM Wiki render + persist)
  ├── runner.py                 subprocess runner + retry
  ├── notebooklm_client.py      Protocol + typed errors
  ├── index_builder.py          Deterministic LLM Wiki index rebuild
  ├── log_builder.py            Append-only log writer
  ├── policy_compare.py         Policy-compare domain logic
  ├── template_renderer.py      Jinja2 entity rendering
  └── ...
config/prompts/                 LLM Wiki priority rules + workflow prompts
docs/llm-wiki-ingestion-standard.md   LLM Wiki ingestion contract
docs/architecture.md            Where LLM Wiki sits in the pipeline
examples/                       Reusable workflow YAML examples
templates/                      Markdown / Jinja templates (LLM Wiki pages)
scripts/bootstrap.sh            Local env + deps setup
tests/                          Unit, phase, integration tests + fakes
artifacts/                      Per-run outputs + staging + manifest
```

---

## LLM Wiki 품질 규칙 / LLM Wiki priority rules

LLM Wiki 는 단순 요약보다 **아래 6가지를 절대 우선**합니다. 이것이 일반 Obsidian vault 와 결정적 차이점입니다.

1. Obligations / prohibitions
2. Retention windows and numeric limits
3. Student / minor safety rules
4. Human review for high-stakes decisions
5. Enterprise controls (SSO, RBAC, audit, retention)
6. Ownership / indemnity / legal risk allocation

> **"Do not let quiz, glossary, or generic marketing text crowd out these items."**
> — `config/prompts/llm_wiki_priority.md`

참고 문서:
- `config/prompts/llm_wiki_priority.md` — 6대 우선순위 규칙
- `docs/llm-wiki-ingestion-standard.md` — ingestion contract
- `docs/architecture.md` — pipeline 내 LLM Wiki 위치

---

## Harness 가 보장하는 것 / What the harness enforces

- NotebookLM protocol boundary + typed runner errors (+ optional retry)
- Flow decomposition into typed phases
- Staged writes + per-run SHA256 manifest
- **Deterministic LLM Wiki index rebuilding** with preamble preservation
- Fake-client full-flow integration test
- Jinja2 entity templates with `StrictUndefined`
- Parser fallback when NotebookLM output lacks a comparison table
- ruff + mypy (strict) + pytest + 80% coverage gate
- GitHub Actions on `ubuntu-latest` and `macos-latest`

---

## 개발 워크플로 / Development workflow

```bash
uv run --python 3.11 --with ruff --with-editable . \
  env PYTHONPATH=src ruff check .

uv run --python 3.11 --with mypy --with-editable . --with types-PyYAML \
  env PYTHONPATH=src mypy src

uv run --python 3.11 --with pytest --with pytest-cov --with-editable . \
  env PYTHONPATH=src python -m pytest
```

---

## Notes

- **Local-first** 실행이 전제 / local-first execution is assumed.
- NotebookLM 인증은 브라우저 로그인 단계 필요 / browser login required.
- 이 저장소의 목표는 "한 번 돌리고 끝" 이 아니라 **LLM Wiki 에 계속 쌓이는 리서치 엔진** 입니다.
- README 는 한·영 병기, 세부 운영 팁은 `docs/` 에 확장.

---

## License

See [LICENSE](./LICENSE).
