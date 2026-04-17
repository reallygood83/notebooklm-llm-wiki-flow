# notebooklm-llm-wiki-flow

NotebookLM → LLM Wiki → Obsidian → qmd 파이프라인을 로컬 우선(local-first)으로 운영하기 위한 Python CLI 프로젝트입니다.

This is a local-first Python CLI project for running a reusable NotebookLM → LLM Wiki → Obsidian → qmd workflow.

===

## 왜 이 프로젝트를 쓰는가? / Why use this project?

한국어
- NotebookLM 결과물을 일회성 리포트로 끝내지 않고, Obsidian 기반 지식 자산으로 축적할 수 있습니다.
- 비교 문서, 체크리스트, 엔티티 문서, 원문 출처 페이지를 한 번의 흐름으로 생성할 수 있습니다.
- qmd 인덱싱까지 이어져 나중에 다시 검색하고 재활용할 수 있습니다.

English
- It turns NotebookLM output from disposable reports into reusable knowledge assets inside an Obsidian vault.
- It generates comparison notes, checklists, entity pages, and raw source pages in one flow.
- It closes the loop with qmd indexing so the result becomes searchable and reusable later.

===

## 사용자가 harness 로 얻는 실익 / Practical user benefits from the harness

이 프로젝트의 핵심은 단순한 스크립트 모음이 아니라, 실제 사용 중 깨지지 않도록 보호하는 harness 를 갖췄다는 점입니다.

### 1. 더 안전한 결과물 / Safer outputs
- staged writes + manifest
- 생성 파일을 바로 실서비스 경로에 덮어쓰지 않고 staging 후 반영합니다.
- 실행 중간에 실패해도 반쯤 써진 wiki 상태를 줄입니다.
- 각 실행마다 `artifacts/<notebook_id>/manifest.json` 이 남아 audit 와 rollback 판단이 쉬워집니다.

### 2. 더 믿을 수 있는 자동화 / More trustworthy automation
- NotebookLM client protocol + typed runner errors
- 외부 CLI 실패가 단순 subprocess 오류로 흩어지지 않고 단계 정보와 함께 수집됩니다.
- fake client integration tests 덕분에 실제 NotebookLM 로그인 없이도 핵심 흐름을 검증할 수 있습니다.

### 3. 협업과 배포가 쉬움 / Easier collaboration and shipping
- ruff + mypy + pytest + coverage gate + GitHub Actions matrix
- 코드 스타일, 타입, 테스트, 커버리지를 로컬과 CI에서 동일하게 검증합니다.
- Ubuntu 와 macOS 모두에서 돌아가는지 자동으로 확인합니다.

### 4. 환경 설정이 덜 헷갈림 / Less confusing setup
- bootstrap hardening + `.env` + `NLWFLOW_*` overrides
- 환경변수 > project.yaml > .env > defaults 우선순위가 명확합니다.
- 설치 실패를 `|| true` 로 숨기지 않아 셋업 문제를 빨리 찾을 수 있습니다.

### 5. 문서 생성 결과의 품질 유지 / More stable note generation quality
- deterministic index update
- template-based entity rendering
- non-table parser fallback
- 즉, 출력 포맷이 조금 흔들려도 wiki 품질이 급격히 무너지지 않게 설계했습니다.

===

## 주요 기능 / Core features

- `nlwflow` Python CLI
- NotebookLM 실행 경계 추상화 (`NotebookLMClient` protocol)
- typed flow phases
- staged writes + manifest
- deterministic wiki index builder
- fake-client integration coverage
- Jinja2-based entity rendering
- parser fallback for non-table NotebookLM reports
- qmd 연동
- GitHub Actions CI with lint, typecheck, tests, and coverage

===

## 빠른 시작 / Quick start

### 한국어
1. 저장소를 클론합니다.
2. `./scripts/bootstrap.sh`
3. `notebooklm login`
4. `./.venv/bin/nlwflow init-config`
5. `./.venv/bin/nlwflow doctor --json`
6. 필요하면 Obsidian starter kit 설치:
   - `./.venv/bin/nlwflow install-obsidian-kit --vault /path/to/vault`
7. 기본 정책 비교 실행:
   - `./.venv/bin/nlwflow run-policy-compare --json`
8. YAML 기반 재사용 워크플로 실행:
   - `./.venv/bin/nlwflow run-from-yaml examples/policy-compare-anthropic-openai-education.yaml --json`

### English
1. Clone the repository.
2. Run `./scripts/bootstrap.sh`
3. Run `notebooklm login`
4. Run `./.venv/bin/nlwflow init-config`
5. Run `./.venv/bin/nlwflow doctor --json`
6. Optionally install the Obsidian starter kit:
   - `./.venv/bin/nlwflow install-obsidian-kit --vault /path/to/vault`
7. Run the built-in policy comparison:
   - `./.venv/bin/nlwflow run-policy-compare --json`
8. Run a reusable YAML workflow:
   - `./.venv/bin/nlwflow run-from-yaml examples/policy-compare-anthropic-openai-education.yaml --json`

===

## CLI 명령 / CLI commands

- `nlwflow doctor`
  - 환경, 경로, qmd/NotebookLM 사용 가능 여부 점검
- `nlwflow init-config`
  - starter config 생성
- `nlwflow plan-policy-compare`
  - 기본 Anthropic vs OpenAI 정책 비교 source pack 출력
- `nlwflow run-policy-compare`
  - NotebookLM notebook 생성, artifact 생성, wiki/Obsidian/qmd 갱신
- `nlwflow run-from-yaml WORKFLOW.yaml`
  - YAML 기반 재사용 워크플로 실행
- `nlwflow install-obsidian-kit`
  - starter vault 구조 설치
- `nlwflow score-report REPORT.md`
  - NotebookLM report 에서 high-signal section 추출

===

## 설정 우선순위 / Configuration precedence

현재 설정 우선순위는 다음과 같습니다.

1. `NLWFLOW_*` environment variables
2. `project.yaml`
3. `.env`
4. built-in defaults

예시
- `NLWFLOW_OBSIDIAN_VAULT`
- `NLWFLOW_WIKI_PATH`
- `NLWFLOW_NOTEBOOKLM_COMMAND`
- `NLWFLOW_QMD_COMMAND`

===

## 현재 harness 에 포함된 보강 / What the current harness already enforces

- NotebookLM protocol boundary
- typed runner errors with step context
- flow decomposition into typed phases
- staged writes + per-run manifest
- deterministic index rebuilding
- fake-client full-flow integration test
- Jinja2 entity templates
- parser fallback when NotebookLM output lacks a comparison table
- ruff / mypy / pytest / coverage gate
- GitHub Actions on ubuntu-latest and macos-latest
- bootstrap script that fails loudly instead of hiding setup problems

===

## 저장소 구조 / Repository layout

- `src/notebooklm_llm_wiki_flow/`
  - Python package and CLI
- `scripts/bootstrap.sh`
  - local setup for Python env, notebooklm-py, Playwright, qmd
- `config/project.example.yaml`
  - editable local config example
- `config/prompts/`
  - workflow prompts and ingestion priority rules
- `examples/`
  - reusable workflow examples
- `templates/`
  - markdown/Jinja templates
- `docs/`
  - architecture, quickstarts, plans, ingestion rules
- `tests/`
  - unit tests, phase tests, integration tests, fake client helpers
- `artifacts/`
  - per-run downloaded outputs, staging, manifest metadata

===

## 품질 규칙 / Quality rules

이 프로젝트는 단순 요약보다 다음 정보를 더 우선합니다.

- obligations / prohibitions
- retention windows and numeric limits
- student and minor safety rules
- human review for high-stakes decisions
- enterprise controls
- ownership, indemnity, and legal risk allocation

관련 문서
- `config/prompts/llm_wiki_priority.md`
- `docs/llm-wiki-ingestion-standard.md`

===

## 개발 워크플로 / Recommended development workflow

1. 로컬에서 수정 / edit locally
2. 테스트 실행 / run lint, mypy, pytest
3. 의미 있는 단위로 커밋 / commit by milestone
4. GitHub 로 push
5. PR 에서 CI 확인

Helpful commands
- `uv run --python 3.11 --with ruff --with-editable . env PYTHONPATH=src ruff check .`
- `uv run --python 3.11 --with mypy --with-editable . --with types-PyYAML env PYTHONPATH=src mypy src`
- `uv run --python 3.11 --with pytest --with pytest-cov --with-editable . env PYTHONPATH=src python -m pytest`

===

## Notes

- local-first execution 전제
- NotebookLM 인증은 브라우저 로그인 단계가 필요함
- 이 저장소는 “한 번 돌리고 끝”이 아니라, 반복 가능한 개인/팀 리서치 엔진을 목표로 함
- README 는 영어와 한국어를 함께 제공하지만, 실제 상세 운영 팁은 `docs/` 에 계속 확장 가능
