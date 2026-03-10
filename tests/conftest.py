"""Shared test fixtures for the current MVP skeleton."""

from pathlib import Path
import sys

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


@pytest.fixture()
def sample_config_path(tmp_path: Path) -> Path:
    """Create a minimal valid config file for CLI and config tests."""

    config_path = tmp_path / "pipeline.yaml"
    config_path.write_text(
        """
dataset:
  dataset_id: fixture_trace
  input_dir: ../data/raw/fixture_trace

output:
  staged_dir: ../data/staged
  processed_dir: ../data/processed
  results_tables_dir: ../results/tables
  results_plots_dir: ../results/plots

sampling:
  rates:
    - 10
    - 100
  method: systematic
""".strip()
        + "\n",
        encoding="utf-8",
    )
    return config_path
