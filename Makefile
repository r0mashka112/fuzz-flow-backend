.PHONY: install dev prod lint format

install:
	poetry install

dev:
	poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

prod:
	poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000

lint:
	poetry run ruff check .

format:
	poetry run ruff format .