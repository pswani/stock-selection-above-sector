#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if ! command -v uv >/dev/null 2>&1; then
  echo "Error: uv is required but not installed. See https://docs.astral.sh/uv/getting-started/installation/" >&2
  exit 1
fi

echo "[validate] Syncing project + dev dependencies from lockfile"
uv sync --dev --frozen

echo "[validate] Python version"
uv run python --version

echo "[validate] Runtime dependency sanity"
uv run python - <<'PY'
import importlib

runtime_required = [
    "numpy",
    "pandas",
    "pydantic",
    "pydantic_settings",
    "scipy",
    "sklearn",
    "yaml",
    "typer",
    "rich",
]

for module in runtime_required:
    importlib.import_module(module)

print("runtime dependency imports: ok")
PY

echo "[validate] Dev-tool versions"
uv run pytest --version
uv run ruff --version
uv run pyright --version

echo "[validate] Project checks"
uv run pytest -q
uv run ruff check .
uv run pyright
