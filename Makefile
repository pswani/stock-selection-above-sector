bootstrap:
	./scripts/bootstrap.sh

validate-env:
	./scripts/validate-env.sh

install:
	uv sync --dev --frozen

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
