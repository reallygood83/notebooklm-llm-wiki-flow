PYTHON ?= python3.13
VENV = .venv

bootstrap:
	./scripts/bootstrap.sh

test:
	$(VENV)/bin/pytest tests

doctor:
	$(VENV)/bin/nlwflow doctor --json

plan-policy-compare:
	$(VENV)/bin/nlwflow plan-policy-compare --json

run-policy-compare:
	$(VENV)/bin/nlwflow run-policy-compare --json

run-from-yaml:
	$(VENV)/bin/nlwflow run-from-yaml $(WORKFLOW) --json

publish:
	./scripts/publish.sh "$(MSG)"
