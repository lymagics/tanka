.PHONY: help unit deep black flake8 ruff lint

.DEFAULT_GOAL := help

help:
	@echo "Tanka development commands"
	@echo ""
	@echo "  make unit      Run unit tests with coverage"
	@echo "  make deep      Run integration tests against live servers"
	@echo "  make black     Check formatting with black"
	@echo "  make flake8    Lint with flake8"
	@echo "  make ruff      Lint with ruff"
	@echo "  make lint      Run black, flake8 and ruff"
	@echo "  make help      Show this help"

unit:
	uv run pytest -m "not deep and not online" --cov=tanka --cov-report=term-missing

deep:
	uv run pytest -m "deep"

black:
	uv run black --check src tests

flake8:
	uv run flake8 src tests

ruff:
	uv run ruff check src tests

lint: black flake8 ruff
