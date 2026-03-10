#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEFAULT_CONFIG="$REPO_ROOT/configs/datasets.batch.yaml"
CONFIG_PATH="$DEFAULT_CONFIG"
PLAN_ONLY=0
NO_CLEAN=0
CLEAN_ONLY=0

usage() {
  cat <<EOF
Usage: $(basename "$0") [CONFIG_PATH] [--plan-only] [--clean-only] [--no-clean]

Runs the batch pipeline wrapper in four steps:
  1. validate-config
  2. plan
  3. clean generated batch outputs
  4. run

Options:
  --plan-only   stop after the plan step
  --clean-only  stop after the cleanup step
  --no-clean    skip the cleanup step before running
  --help        show this help text

If CONFIG_PATH is omitted, the script uses:
  $DEFAULT_CONFIG
EOF
}

while (($# > 0)); do
  case "$1" in
    --plan-only)
      PLAN_ONLY=1
      shift
      ;;
    --clean-only)
      CLEAN_ONLY=1
      shift
      ;;
    --no-clean)
      NO_CLEAN=1
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    -*)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
    *)
      if [[ "$CONFIG_PATH" != "$DEFAULT_CONFIG" ]]; then
        echo "Only one config path may be provided." >&2
        usage >&2
        exit 1
      fi
      CONFIG_PATH="$1"
      shift
      ;;
  esac
done

if [[ "$PLAN_ONLY" -eq 1 && "$CLEAN_ONLY" -eq 1 ]]; then
  echo "--plan-only and --clean-only cannot be used together." >&2
  usage >&2
  exit 1
fi

if [[ -x "$REPO_ROOT/.venv/bin/python" ]]; then
  PYTHON_BIN="$REPO_ROOT/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python)"
else
  echo "No Python interpreter was found. Create a venv or install Python first." >&2
  exit 1
fi

RUNNER="$REPO_ROOT/scripts/run_dataset_batches.py"

if [[ -z "${NETWORK_ANALYSIS_PROGRESS+x}" ]]; then
  export NETWORK_ANALYSIS_PROGRESS=1
fi

if ! "$PYTHON_BIN" - <<'PY' >/dev/null 2>&1
import importlib.util
raise SystemExit(0 if importlib.util.find_spec("tqdm") else 1)
PY
then
  echo "Warning: tqdm is not installed for $PYTHON_BIN; using text progress fallback. Run 'pip install -r requirements.txt' to enable tqdm bars." >&2
fi

echo "[1/4] Validating batch config: $CONFIG_PATH"
"$PYTHON_BIN" "$RUNNER" --config "$CONFIG_PATH" validate-config

echo "[2/4] Rendering batch plan"
"$PYTHON_BIN" "$RUNNER" --config "$CONFIG_PATH" plan

if [[ "$PLAN_ONLY" -eq 1 ]]; then
  echo "Plan-only mode requested; skipping batch execution."
  exit 0
fi

if [[ "$NO_CLEAN" -eq 0 ]]; then
  echo "[3/4] Cleaning generated batch outputs"
  "$PYTHON_BIN" "$RUNNER" --config "$CONFIG_PATH" clean
else
  echo "[3/4] Skipping cleanup (--no-clean)"
fi

if [[ "$CLEAN_ONLY" -eq 1 ]]; then
  echo "Clean-only mode requested; skipping batch execution."
  exit 0
fi

echo "[4/4] Running batch pipeline"
"$PYTHON_BIN" "$RUNNER" --config "$CONFIG_PATH" run
