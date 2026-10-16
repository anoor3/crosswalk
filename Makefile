.PHONY: verify test lint types

verify:
	sh scripts/verify.sh

test:
	.venv/bin/pytest -q

lint:
	.venv/bin/ruff check .

types:
	.venv/bin/mypy packages
