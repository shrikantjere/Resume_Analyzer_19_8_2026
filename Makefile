.PHONY: install install-dev test test-unit test-integration test-e2e lint format run clean migrate

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt
	pre-commit install

test:
	pytest tests/

test-unit:
	pytest tests/unit/ -v

test-integration:
	pytest tests/integration/ -v

test-e2e:
	pytest tests/e2e/ -v

lint:
	ruff check .
	mypy .

format:
	black .

run:
	streamlit run app.py

clean:
	rm -rf __pycache__ */__pycache__ .pytest_cache .mypy_cache
	rm -rf data/uploads/* data/reports/*
	rm -rf logs/*.log
	rm -rf htmlcov .coverage

migrate:
	python -c "from core.db import DatabaseManager; DatabaseManager().run_migrations()"