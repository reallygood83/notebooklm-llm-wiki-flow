# notebooklm-llm-wiki-flow

[![CI](https://github.com/reallygood83/notebooklm-llm-wiki-flow/actions/workflows/ci.yml/badge.svg)](https://github.com/reallygood83/notebooklm-llm-wiki-flow/actions)

NotebookLM → LLM Wiki → Obsidian → qmd 파이프라인을 **local-first**로 운영하기 위한 Python CLI 프로젝트입니다.
A local-first Python CLI for running a reusable NotebookLM → LLM Wiki → Obsidian → qmd workflow.

---

## 왜 이 프로젝트를 쓰는가? / Why use this project?

### 🇰🇷 한국어
NotebookLM 은 강력하지만 결과물이 **일회성 리포트**로 끝나는 한계가 있습니다.
이 프로젝트는 그 결과물을 **지식 자산**으로 축적하기 위한 local-first 파이프라인입니다.

- NotebookLM 출력을 Obsidian vault 로 구조화해 축적합니다.
- 비교 문서, 체크리스트, 엔티티 문서, 원문 소스 페이지를 **한 번의 실행**으로 생성합니다.
- qmd 인덱싱까지 이어져, 나중에 다시 검색하고 재사용할 수 있습니다.
- **YAML 기반 재사용 워크플로**로 분석 주제를 계속 확장할 수 있습니다.

### 🇬🇧 English
NotebookLM is powerful but its output usually ends up as **one-off reports**.
This project is a local-first pipeline that converts those outputs into a **reusable knowledge asset**.

- Structured Obsidian-vault-aware output instead of disposable notes.
- Generates comparison notes, checklists, entity pages, and raw source pages in **one flow**.
- Closes the loop with qmd indexing so results become searchable and reusable later.
- **YAML-based reusable workflows** let you scale the same flow across new topics.

---

## 사용자가 얻는 실익 / Practical user benefits

NotebookLM을 CLI 파이프라인으로 감싸서 얻는 **구체적 이득**입니다.

### 1. 토큰/비용 절감 — Token and cost savings
- NotebookLM은 자체 grounding 을 하므로 Claude/GPT API 로 긴 원문 전체를 재전송할 필요가 없습니다.
- 핵심 파싱은 NotebookLM이 맡고, 이후 단계는 **deterministic template** 으로 처리해 LLM 호출을 최소화합니다.
- 한 번 notebook을 만들면 다시 대화·재분석할 때 인증·세션만 유지하면 됩니다.

### 2. 검증 가능한 grounding — Verifiable grounding
- 각 비교 문서는 NotebookLM report + Q&A + 원문 source URL 을 모두 **한 곳에 묶어 저장**합니다.
- 사용자는 "이 주장 어디서 나왔지?" 라는 질문을 **원문 링크**로 즉시 추적할 수 있습니다.
- `source_notes` / `source_urls` 프론트매터가 모든 파일에 들어갑니다.

### 3. 지식 누적 — Knowledge accumulation
- 결과물이 Obsidian vault 로 바로 들어가므로, 링크·태그·백링크로 자연스럽게 축적됩니다.
- `## Entities` / `## Comparisons` / `## Queries` 섹션이 있는 **deterministic index** 가 자동 재생성됩니다.
- qmd 를 통해 vault 전체가 재검색 가능해집니다.

### 4. 자동화 신뢰성 — Automation reliability
- `NotebookLMClient` Protocol 로 CLI 경계를 추상화하여, 실제 브라우저 로그인 없이도 **fake client** 로 전 과정을 테스트할 수 있습니다.
- `NotebookLMRunner` 는 subprocess 실패를 **typed error + step 컨텍스트**로 감쌉니다.
- 옵션으로 **retry/backoff** 를 활성화할 수 있어, 네트워크 일시 장애에 탄력적입니다.

### 5. 안전한 출력 — Safer outputs
- **Staged writes + manifest** — 생성 파일은 staging 을 거쳐 목적지에 반영되고, 중간 실패시 반쯤 써진 wiki 상태를 줄입니다.
- 매 실행마다 `artifacts/<notebook_id>/manifest.json` 이 남아 audit / rollback 이 쉬워집니다.
- Jinja2 `StrictUndefined` 템플릿으로 누락 필드는 즉시 감지됩니다.

### 6. 협업과 재현성 — Collaboration and reproducibility
- ruff + mypy (strict) + pytest + **coverage gate 80%** + GitHub Actions matrix (Ubuntu + macOS).
- 로컬과 CI 에서 동일 기준으로 검증됩니다.
- 환경변수 > `project.yaml` > `.env` > defaults 우선순위가 **명시적**이라 팀 설정이 흔들리지 않습니다.

### 7. 품질 유지 — Stable note quality
- Parser fallback: NotebookLM 출력에 비교표가 없어도 bullet 기반 fallback 이 동작합니다.
- Deterministic index rebuilder: preamble 보존 + dedup 으로 수동 편집이 날아가지 않습니다.
- YAML 기반 entity rendering 으로 새 주제 확장 시 코드 변경 없이 meta 만 수정하면 됩니다.

---

## 주요 기능 / Core features

- `nlwflow` Python CLI with Typer + Rich
- `NotebookLMClient` Protocol + typed runner errors + optional retry
- Typed flow phases (`NotebookRunResult`, `ArtifactExportResult`, `WikiRenderResult`, `PersistResult`, `IndexUpdateResult`)
- Staged writes + SHA256 manifest for each run
- Deterministic index rebuilder with preamble preservation
- Fake-client integration coverage
- Jinja2-based entity rendering (`StrictUndefined`)
- Parser fallback for non-table NotebookLM reports
- Obsidian starter kit installer
- qmd integration
- GitHub Actions CI matrix (Ubuntu + macOS) with lint, typecheck, tests, coverage

---

## 빠른 시작 / Quick start

### 🇰🇷 한국어
1. 저장소 클론
2. `./scripts/bootstrap.sh` (Python env + notebooklm-py + Playwright + qmd 설치)
3. `notebooklm login` — 브라우저 로그인 1회
4. `./.venv/bin/nlwflow init-config`
5. `./.venv/bin/nlwflow doctor --json` 으로 환경 점검
6. (선택) Obsidian starter kit 설치
   - `./.venv/bin/nlwflow install-obsidian-kit --vault /path/to/vault`
7. 기본 정책 비교 실행
   - `./.venv/bin/nlwflow run-policy-compare --json`
8. YAML 기반 재사용 워크플로 실행
   - `./.venv/bin/nlwflow run-from-yaml examples/policy-compare-anthropic-openai-education.yaml --json`

### 🇬🇧 English
1. Clone the repository
2. Run `./scripts/bootstrap.sh` to install the Python env, notebooklm-py, Playwright, and qmd
3. Run `notebooklm login` (browser login, once)
4. Run `./.venv/bin/nlwflow init-config`
5. Run `./.venv/bin/nlwflow doctor --json`
6. (Optional) install the Obsidian starter kit:
   - `./.venv/bin/nlwflow install-obsidian-kit --vault /path/to/vault`
7. Run the built-in policy comparison:
   - `./.venv/bin/nlwflow run-policy-compare --json`
8. Run a reusable YAML workflow:
   - `./.venv/bin/nlwflow run-from-yaml examples/policy-compare-anthropic-openai-education.yaml --json`

---

## CLI 명령 / CLI commands

| Command | Purpose |
|---------|---------|
| `nlwflow --version` | 버전 출력 / print version |
| `nlwflow doctor` | 환경, 경로, qmd/NotebookLM 사용 가능 여부 점검 |
| `nlwflow init-config` | starter config 생성 |
| `nlwflow plan-policy-compare` | 기본 Anthropic vs OpenAI 정책 비교 source pack 출력 |
| `nlwflow run-policy-compare` | NotebookLM notebook 생성, artifact 생성, wiki/Obsidian/qmd 갱신 |
| `nlwflow run-from-yaml WORKFLOW.yaml` | YAML 기반 재사용 워크플로 실행 |
| `nlwflow install-obsidian-kit` | starter vault 구조 설치 |
| `nlwflow score-report REPORT.md` | NotebookLM report 에서 high-signal section 추출 |

---

## 설정 우선순위 / Configuration precedence

1. `NLWFLOW_*` 환경변수 / environment variables
2. `project.yaml`
3. `.env`
4. 내장 기본값 / built-in defaults

주요 환경변수 / key env vars:
- `NLWFLOW_OBSIDIAN_VAULT`
- `NLWFLOW_WIKI_PATH`
- `NLWFLOW_NOTEBOOKLM_COMMAND`
- `NLWFLOW_QMD_COMMAND`
- `NLWFLOW_QMD_COLLECTION`

---

## Harness 가 보장하는 것 / What the harness already enforces

- NotebookLM protocol boundary + typed runner errors (+ optional retry)
- Flow decomposition into typed phases
- Staged writes + per-run SHA256 manifest
- Deterministic index rebuilding with preamble preservation
- Fake-client full-flow integration test
- Jinja2 entity templates with `StrictUndefined`
- Parser fallback when NotebookLM output lacks a comparison table
- ruff + mypy + pytest + 80% coverage gate
- GitHub Actions on `ubuntu-latest` and `macos-latest`
- Bootstrap script that **fails loudly** instead of hiding setup problems

---

## 저장소 구조 / Repository layout

```
src/notebooklm_llm_wiki_flow/   Python package and CLI
  ├── flow.py                   Typed-phase orchestrator
  ├── runner.py                 subprocess runner + retry
  ├── notebooklm_client.py      Protocol + typed errors
  ├── index_builder.py          Deterministic wiki index rebuild
  ├── log_builder.py            Append-only log writer
  ├── policy_compare.py         Policy-compare domain logic
  ├── template_renderer.py      Jinja2 entity rendering
  └── ...
scripts/bootstrap.sh            Local env + deps setup
config/project.example.yaml     Editable local config
config/prompts/                 Workflow prompts + priority rules
examples/                       Reusable workflow YAML examples
templates/                      Markdown / Jinja templates
docs/                           Architecture, quickstarts, plans
tests/                          Unit, phase, integration tests + fakes
artifacts/                      Per-run outputs + staging + manifest
```

---

## 품질 규칙 / Quality rules

단순 요약보다 다음을 더 우선합니다 / Priority over shallow summaries:

- obligations / prohibitions
- retention windows and numeric limits
- student and minor safety rules
- human review for high-stakes decisions
- enterprise controls
- ownership, indemnity, and legal risk allocation

참고 문서 / reference:
- `config/prompts/llm_wiki_priority.md`
- `docs/llm-wiki-ingestion-standard.md`

---

## 개발 워크플로 / Development workflow

1. 로컬에서 수정 / edit locally
2. Lint + typecheck + pytest 실행 / run quality gates
3. 의미 있는 단위 커밋 / commit by milestone
4. GitHub push
5. PR 에서 CI 확인

도우미 명령어 / helpful commands:

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

- **Local-first** 실행이 전제입니다 / local-first execution is assumed.
- NotebookLM 인증은 브라우저 로그인 단계가 필요합니다 / NotebookLM login requires a browser step.
- 이 저장소는 "한 번 돌리고 끝" 이 아니라 **반복 가능한 개인/팀 리서치 엔진** 을 목표로 합니다.
- README 는 한·영 병기하며, 상세 운영 팁은 `docs/` 에 계속 확장됩니다.

---

## License

See [LICENSE](./LICENSE).
