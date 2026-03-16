#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if ! command -v uv >/dev/null 2>&1; then
  echo "Error: uv is required but not installed. See https://docs.astral.sh/uv/getting-started/installation/" >&2
  exit 1
fi

PYTHON_VERSION="$(cat .python-version)"

echo "[bootstrap] Ensuring Python ${PYTHON_VERSION} is available via uv"
uv python install "${PYTHON_VERSION}"

echo "[bootstrap] Syncing project + dev dependencies from lockfile"
uv sync --dev --frozen

echo "[bootstrap] Validating runtime imports"
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

print("runtime imports: ok")
PY

echo "[bootstrap] Validating dev-tool availability"
uv run pytest --version >/dev/null
uv run ruff --version >/dev/null
uv run pyright --version >/dev/null

echo "[bootstrap] Completed successfully"
