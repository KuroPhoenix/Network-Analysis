"""Shared test fixtures for the Stage 1 skeleton."""

from pathlib import Path

import pytest


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

