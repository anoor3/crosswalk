.PHONY: verify test lint types test-api test-service

verify:
	sh scripts/verify.sh

test:
	.venv/bin/pytest -q

lint:
	.venv/bin/ruff check .

types:
	.venv/bin/mypy packages

test-api:
	.venv/bin/pytest apps/api/tests -q

test-service:
	.venv/bin/pytest packages/service/tests -q
