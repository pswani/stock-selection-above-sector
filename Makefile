install:
	uv sync --dev

test:
	uv run pytest -q

lint:
	uv run ruff check .

format:
	uv run ruff format .

typecheck:
	uv run pyright

all:
	$(MAKE) lint && $(MAKE) test
