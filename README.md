# notebooklm-llm-wiki-flow

[![CI](https://github.com/reallygood83/notebooklm-llm-wiki-flow/actions/workflows/ci.yml/badge.svg)](https://github.com/reallygood83/notebooklm-llm-wiki-flow/actions)

한국어 문서입니다.
For English, see: [README.en.md](./README.en.md)

===

소개

notebooklm-llm-wiki-flow 는 NotebookLM 결과물을 일회성 리포트로 끝내지 않고,
LLM Wiki → Obsidian → qmd 로 이어지는 재사용 가능한 지식 자산으로 바꾸는 local-first Python CLI 입니다.

핵심 개념은 NotebookLM 자체보다 LLM Wiki 입니다.
NotebookLM 은 자료를 모으고 초안을 만드는 단계이고,
실제로 지식이 축적되는 곳은 LLM Wiki 입니다.

===

이 프로젝트가 하는 일

1. NotebookLM 에 원문 URL/PDF 등을 넣습니다.
2. report / mind map / Q&A 같은 산출물을 받습니다.
3. 핵심 내용만 추려 LLM Wiki 구조로 저장합니다.
4. Obsidian 에서 사람이 읽고 수정할 수 있게 만듭니다.
5. qmd 로 다시 인덱싱해서 검색 가능하게 만듭니다.

===

LLM Wiki 란?

LLM Wiki 는 LLM 출력 전체를 저장하는 곳이 아닙니다.
의사결정에 실제로 필요한 정보만 구조화해서 남기는 knowledge layer 입니다.

저장되는 대표 페이지 유형
- Raw source
  - 원문과 출처 정보 보관
- Entity
  - 회사, 제품, 개념 단위 지식 축적
- Comparison
  - 두 정책, 제품, 문서의 비교 결과
- Query / Checklist
  - 재사용 가능한 실행 체크리스트

===

사용자가 얻는 실익

1. 결과물이 안전합니다
- staged writes 로 중간 실패 시 반쯤 써진 파일 상태를 줄입니다.
- manifest.json 이 남아 실행 결과를 추적하기 쉽습니다.

2. 자동화가 더 믿을 만합니다
- NotebookLM CLI 실패가 typed error 와 step 정보로 잡힙니다.
- fake client integration test 로 실제 NotebookLM 없이도 핵심 흐름을 검증합니다.

3. 설정이 덜 헷갈립니다
- 우선순위가 명확합니다.
  - environment variables > project.yaml > .env > defaults
- bootstrap 이 실패를 숨기지 않습니다.

4. 문서 품질이 더 안정적입니다
- deterministic index rebuild
- template-based entity rendering
- non-table parser fallback

5. 협업과 배포가 쉽습니다
- ruff
- mypy
- pytest
- coverage gate
- GitHub Actions on Ubuntu + macOS

===

주요 기능

- `nlwflow` CLI
- NotebookLM client protocol
- typed flow phases
- staged writes + manifest
- deterministic wiki index update
- fake-client integration test
- Jinja2 entity templates
- parser fallback for non-table reports
- qmd integration
- GitHub Actions CI

===

사전 요구사항

- Python 3.11+
- Node.js 20+ 와 npm (qmd 인덱서용, `INSTALL_QMD_GLOBAL=0` 으로 건너뛸 수 있음)
- pipx (옵션 — `USE_PIPX=1` 모드로 격리 설치할 때만 필요)

===

설치 방법 — 두 가지 경로

notebooklm-py 는 이제 `[notebooklm]` extra 로 자동 설치됩니다.

**A. 한 줄 설치 (권장) — `./scripts/bootstrap.sh`**

아래를 자동으로 다 해줍니다.

1. `.venv` 생성 + 이 프로젝트 editable 설치
2. `pip install -e ".[dev,notebooklm]"` — nlwflow + **notebooklm-py** + Playwright 모두 venv 안에
3. `python -m playwright install chromium`
4. `npm install -g @tobilu/qmd` (옵션)

**B. 직접 pip 로 설치**

```bash
python3.11 -m venv .venv
./.venv/bin/pip install -e ".[notebooklm]"
./.venv/bin/python -m playwright install chromium
# qmd 는 별도: npm install -g @tobilu/qmd
```

**C. 격리 설치를 원한다면 (예전 방식)**

```bash
USE_PIPX=1 ./scripts/bootstrap.sh
```

이 경우 `notebooklm-py` 는 pipx 로 `~/.local/pipx/venvs/notebooklm-py/` 에 별도 격리됩니다.

===

빠른 시작

1. 저장소 클론
2. `./scripts/bootstrap.sh`
3. `notebooklm login` — 브라우저 로그인 1회
4. `./.venv/bin/nlwflow init-config`
5. `./.venv/bin/nlwflow doctor --json`
6. 필요하면 starter kit 설치
   - `./.venv/bin/nlwflow install-obsidian-kit --vault /path/to/vault`
7. 기본 실행
   - `./.venv/bin/nlwflow run-policy-compare --json`
8. YAML 워크플로 실행
   - `./.venv/bin/nlwflow run-from-yaml examples/policy-compare-anthropic-openai-education.yaml --json`

===

CLI 명령

- `nlwflow --version`
  - 버전 출력
- `nlwflow doctor`
  - 환경과 경로 점검
- `nlwflow init-config`
  - 설정 파일 생성
- `nlwflow plan-policy-compare`
  - 기본 비교 source pack 출력
- `nlwflow run-policy-compare`
  - NotebookLM 실행 + wiki/obsidian/qmd 반영
- `nlwflow run-from-yaml WORKFLOW.yaml`
  - 재사용 가능한 YAML 워크플로 실행
- `nlwflow install-obsidian-kit`
  - starter vault 설치
- `nlwflow score-report REPORT.md`
  - high-signal section 추출

===

설정 우선순위

1. `NLWFLOW_*` 환경변수
2. `project.yaml`
3. `.env`
4. 기본값

자주 쓰는 환경변수
- `NLWFLOW_OBSIDIAN_VAULT`
- `NLWFLOW_WIKI_PATH`
- `NLWFLOW_NOTEBOOKLM_COMMAND`
- `NLWFLOW_QMD_COMMAND`
- `NLWFLOW_QMD_COLLECTION`

===

프로젝트 구조

- `src/notebooklm_llm_wiki_flow/`
  - Python package 와 CLI
- `config/`
  - 설정과 프롬프트
- `examples/`
  - 재사용 가능한 workflow 예시
- `templates/`
  - markdown / Jinja 템플릿
- `docs/`
  - architecture, quickstart, ingestion rule
- `tests/`
  - unit / phase / integration tests
- `artifacts/`
  - 실행 산출물, staging, manifest

===

현재 harness 가 보장하는 것

- protocol-based NotebookLM boundary
- typed runner errors
- typed flow phases
- staged writes + per-run manifest
- deterministic index rebuilding
- fake-client full-flow integration tests
- template rendering with Jinja2
- parser fallback when NotebookLM output has no comparison table
- ruff + mypy + pytest + coverage gate
- GitHub Actions on ubuntu-latest and macos-latest

===

언제 유용한가?

- 정책 비교 리서치
- 벤더 비교
- 교육/의료/엔터프라이즈 AI 거버넌스 분석
- Obsidian 기반 개인 지식 DB 구축
- 반복 가능한 research-to-knowledge 파이프라인이 필요할 때

===

License

See [LICENSE](./LICENSE).
