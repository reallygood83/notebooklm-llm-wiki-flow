# notebooklm-llm-wiki-flow fast hardening implementation plan

> For Hermes: Use subagent-driven-development skill to implement this plan task-by-task.

Goal: turn the current working scaffold into a more reliable execution engine by first strengthening the external NotebookLM boundary, then the flow orchestration boundary, then the quality harness.

Architecture: keep the current local-first Typer CLI and NotebookLM workflow, but split execution into explicit phases with typed inputs and outputs. Replace direct subprocess coupling with a protocol-based client boundary so the main flow can be tested with fakes. Make file writes safer, index updates deterministic, and quality gates automatic.

Tech stack: Python 3.11+, Typer, PyYAML, pytest, pytest-cov, ruff, mypy, Jinja2, qmd, notebooklm-py.

---

## Success criteria

- flow.py no longer depends on direct subprocess semantics for NotebookLM execution.
- At least one fake-client end-to-end flow test exists and passes locally.
- index.md update logic no longer hardcodes total page count.
- wiki writes use staged output plus manifest metadata.
- CI runs lint, type check, tests, and coverage on ubuntu and macOS.
- entity page text is template-driven rather than hardcoded inside policy_compare.py.

---

## Phase 1 — Execution boundary hardening

### Task 1: Introduce a NotebookLM client protocol and typed errors

Objective: remove direct flow dependence on NotebookLMRunner internals so tests can swap in a fake implementation.

Files:
- Create: src/notebooklm_llm_wiki_flow/notebooklm_client.py
- Modify: src/notebooklm_llm_wiki_flow/runner.py
- Modify: src/notebooklm_llm_wiki_flow/flow.py
- Test: tests/test_runner_protocol.py

Steps:
1. Create NotebookLMClient Protocol with methods matching the current flow needs:
   - create_notebook
   - add_source
   - wait_source
   - generate_report
   - wait_artifact
   - generate_mind_map
   - ask
   - download_report
   - download_mind_map
2. Add typed exceptions in the same module:
   - NotebookLMError
   - NotebookLMCommandError
   - NotebookLMTimeoutError
3. Refactor NotebookLMRunner to implement the protocol and wrap subprocess failures with step-aware context.
4. Update flow.py so _run_plan accepts a client object or factory instead of constructing NotebookLMRunner inline.
5. Add unit tests that assert subprocess failures are converted into typed exceptions with command and step metadata.

Verification:
- Run: ./.venv/bin/pytest -q tests/test_runner_protocol.py
- Expected: protocol tests pass and failures are wrapped predictably.

Commit:
- feat: add notebooklm client protocol and typed runner errors

### Task 2: Add retry and timeout configuration at the client boundary

Objective: centralize flakiness handling where external CLI calls happen.

Files:
- Modify: src/notebooklm_llm_wiki_flow/runner.py
- Modify: src/notebooklm_llm_wiki_flow/config.py
- Modify: config/project.example.yaml
- Modify: pyproject.toml
- Test: tests/test_runner_protocol.py

Steps:
1. Add config fields for source_wait_timeout, artifact_wait_timeout, retry_attempts, and retry_backoff_seconds.
2. Add tenacity to dependencies.
3. Apply retry only to external-command methods that are safe to retry.
4. Keep create/download calls explicit and fail-fast if they are not idempotent enough.
5. Extend tests to verify retryable and non-retryable behavior boundaries.

Verification:
- Run: ./.venv/bin/pytest -q tests/test_runner_protocol.py
- Run: ./.venv/bin/nlwflow doctor --json
- Expected: config still loads and retry settings appear sane.

Commit:
- feat: add retryable notebooklm command boundary

---

## Phase 2 — Flow decomposition and deterministic writes

### Task 3: Split _run_plan into phase functions with typed results

Objective: remove the 133-line god function and make each phase testable in isolation.

Files:
- Create: src/notebooklm_llm_wiki_flow/flow_models.py
- Modify: src/notebooklm_llm_wiki_flow/flow.py
- Test: tests/test_flow_phases.py

Steps:
1. Create dataclasses for phase outputs:
   - NotebookRunResult
   - ArtifactExportResult
   - WikiRenderResult
   - PersistResult
   - IndexUpdateResult
2. Extract private phase functions from _run_plan:
   - _run_notebook_phase
   - _export_artifacts_phase
   - _render_wiki_phase
   - _persist_outputs_phase
   - _update_indexes_phase
3. Keep _run_plan as a small coordinator that passes typed results between phases.
4. Ensure each phase returns explicit paths, created files, and any update metadata.
5. Add unit tests for each phase using fake inputs rather than real subprocesses.

Verification:
- Run: ./.venv/bin/pytest -q tests/test_flow_phases.py
- Expected: each phase test passes independently.

Commit:
- refactor: split flow orchestration into typed phases

### Task 4: Replace fragile index mutation with deterministic index rendering

Objective: eliminate total page count hardcoding and reduce dependence on exact section order.

Files:
- Modify: src/notebooklm_llm_wiki_flow/flow.py
- Create: src/notebooklm_llm_wiki_flow/index_builder.py
- Test: tests/test_index_builder.py
- Optional doc update: docs/architecture.md

Steps:
1. Move index behavior out of _update_index into a small builder module.
2. Read the current index once, parse known sections, and rebuild the managed portion deterministically.
3. Compute total pages dynamically from managed wiki paths instead of hardcoding 13.
4. If required sections are missing, create them rather than silently skipping updates.
5. Keep a clear separation between user-editable freeform content and managed sections.

Verification:
- Run: ./.venv/bin/pytest -q tests/test_index_builder.py
- Expected: existing index variants update safely and total pages are dynamic.

Commit:
- fix: make wiki index updates deterministic and dynamic

### Task 5: Add staged writes and manifest output

Objective: avoid half-written wiki states and create an audit trail for each run.

Files:
- Create: src/notebooklm_llm_wiki_flow/persistence.py
- Modify: src/notebooklm_llm_wiki_flow/flow.py
- Test: tests/test_persistence.py
- Example output path: artifacts/<notebook_id>/manifest.json

Steps:
1. Write all generated note content into a staging directory under artifacts/<notebook_id>/staging.
2. Promote staged files into final wiki targets only after all content is ready.
3. Write manifest.json containing notebook_id, generated files, timestamps, and checksums.
4. Return manifest path in the final CLI payload.
5. Add failure tests that confirm no partial final writes are left behind when staging fails.

Verification:
- Run: ./.venv/bin/pytest -q tests/test_persistence.py
- Expected: failed writes do not leave half-updated final wiki files.

Commit:
- feat: add staged writes and per-run manifest

### Task 6: Add a fake-client end-to-end flow test

Objective: cover the most important path without calling the real NotebookLM CLI.

Files:
- Create: tests/fakes/fake_notebooklm_client.py
- Create: tests/test_flow_integration_fake_client.py
- Modify: src/notebooklm_llm_wiki_flow/flow.py if dependency injection needs small adjustments

Steps:
1. Create a fake client that returns deterministic notebook, source, report, mind-map, and Q&A payloads.
2. Run the full flow against tmp_path-based wiki and artifact directories.
3. Assert output files exist:
   - raw source page
   - raw report page
   - comparison page
   - checklist page
   - inbox note
   - manifest.json
4. Assert index.md and log.md were updated correctly.
5. Assert qmd update can be disabled cleanly in tests.

Verification:
- Run: ./.venv/bin/pytest -q tests/test_flow_integration_fake_client.py
- Expected: one fake full-flow test passes without notebooklm installed.

Commit:
- test: add fake client integration coverage for full flow

---

## Phase 3 — Quality harness quick wins

### Task 7: Add lint, type check, and coverage gates

Objective: catch regressions before they ship.

Files:
- Modify: pyproject.toml
- Modify: .github/workflows/ci.yml
- Create: .pre-commit-config.yaml

Steps:
1. Add dev dependencies:
   - ruff
   - mypy
   - pytest-cov
2. Add ruff configuration and a minimal mypy strict target for src/notebooklm_llm_wiki_flow.
3. Set pytest addopts to include coverage and a fail-under target of 80.
4. Expand CI to a matrix on ubuntu-latest and macos-latest.
5. Add pre-commit hooks for ruff and mypy.

Verification:
- Run: ./.venv/bin/ruff check .
- Run: ./.venv/bin/mypy src
- Run: ./.venv/bin/pytest
- Expected: all checks pass locally.

Commit:
- ci: add lint typecheck and coverage gates

### Task 8: Fix bootstrap failure masking and environment loading

Objective: make setup failures visible and config override behavior explicit.

Files:
- Modify: scripts/bootstrap.sh
- Modify: src/notebooklm_llm_wiki_flow/config.py
- Modify: config/project.example.yaml
- Modify: pyproject.toml
- Test: tests/test_config.py

Steps:
1. Remove silent || true from bootstrap steps that must fail loudly.
2. Keep optional installs explicitly marked as optional rather than silently swallowed.
3. Add python-dotenv and NLWFLOW_* environment override support in config.py.
4. Document precedence order: env vars, project config, defaults.
5. Add config tests for env override behavior.

Verification:
- Run: ./.venv/bin/pytest -q tests/test_config.py
- Run: ./scripts/bootstrap.sh on a prepared machine when ready
- Expected: failures are visible and config overrides are deterministic.

Commit:
- fix: harden bootstrap and config environment overrides

---

## Phase 4 — Content rendering cleanup

### Task 9: Externalize entity rendering into templates

Objective: separate policy data extraction from note presentation.

Files:
- Create: templates/entity.md.j2
- Create: src/notebooklm_llm_wiki_flow/template_renderer.py
- Modify: src/notebooklm_llm_wiki_flow/policy_compare.py
- Modify: pyproject.toml if package data needs inclusion
- Test: tests/test_policy_compare.py

Steps:
1. Add Jinja2 dependency.
2. Replace render_openai_entity and render_anthropic_entity hardcoded prose with template rendering from structured input data.
3. Keep the current summaries as initial fallback seed data only if extracted content is missing.
4. Ensure created and updated timestamps are fully dynamic.
5. Extend tests to assert rendered entities use template variables correctly.

Verification:
- Run: ./.venv/bin/pytest -q tests/test_policy_compare.py
- Expected: entity rendering remains stable but no longer depends on hardcoded note bodies.

Commit:
- refactor: move entity note rendering into jinja templates

### Task 10: Add parser warnings and text fallback extraction

Objective: prevent silent failure when NotebookLM output format drifts.

Files:
- Modify: src/notebooklm_llm_wiki_flow/policy_compare.py
- Modify: src/notebooklm_llm_wiki_flow/report_parser.py
- Test: tests/test_policy_compare.py

Steps:
1. When table extraction finds no valid rows, emit a warning through logging.
2. Add a text-based fallback that scans report sections for key policy dimensions.
3. Surface fallback usage in the final run payload or manifest.
4. Add tests for both markdown table and non-table reports.

Verification:
- Run: ./.venv/bin/pytest -q tests/test_policy_compare.py
- Expected: non-table reports still produce useful key differences or explicit warnings.

Commit:
- fix: add parser fallback for non-table notebooklm reports

---

## Recommended implementation order

Day 1
1. Task 1
2. Task 3
3. Task 6

Day 2
4. Task 4
5. Task 5
6. Task 7

Day 3
7. Task 8
8. Task 9
9. Task 10
10. Task 2 if retry tuning still needs to be staged after protocol extraction

Reasoning:
- The first win is testability.
- The second win is deterministic writes and index safety.
- The third win is automation discipline and maintainability.

---

## Minimum fast-hardening slice

If only one short sprint is available, do exactly these first four tasks:
- Task 1: NotebookLM client protocol
- Task 3: flow phase split
- Task 4: deterministic index update
- Task 6: fake-client end-to-end test

That slice gives the biggest reliability gain with the smallest dependency increase.

---

## Commands checklist

Use these commands during implementation:
- ./.venv/bin/pytest -q
- ./.venv/bin/pytest -q tests/test_runner_protocol.py
- ./.venv/bin/pytest -q tests/test_flow_phases.py
- ./.venv/bin/pytest -q tests/test_flow_integration_fake_client.py
- ./.venv/bin/ruff check .
- ./.venv/bin/mypy src
- git status --short

---

## Done definition

The fast-hardening pass is complete when:
- fake-client full-flow tests pass locally
- _run_plan is a small coordinator rather than a large god function
- index updates are dynamic and deterministic
- manifest.json is emitted for each run
- CI enforces lint, types, tests, and coverage on both ubuntu and macOS
- entity rendering is template-driven and timestamp-safe
