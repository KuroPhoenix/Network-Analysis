"""Tests for the shared config loader."""

from pathlib import Path

import pytest

from network_analysis.shared.config import ConfigError, load_pipeline_config
from network_analysis.shared.constants import (
    DEFAULT_FLOW_KEY_FIELDS,
    DEFAULT_INACTIVITY_TIMEOUT_SECONDS,
)
from network_analysis.shared.types import SizeBasis


def test_load_pipeline_config_applies_defaults_and_adds_baseline(sample_config_path: Path) -> None:
    config = load_pipeline_config(sample_config_path)

    assert config.dataset.dataset_id == "fixture_trace"
    assert config.methodology.flow_key_fields == DEFAULT_FLOW_KEY_FIELDS
    assert config.methodology.inactivity_timeout_seconds == DEFAULT_INACTIVITY_TIMEOUT_SECONDS
    assert config.methodology.size_basis == SizeBasis.PACKETS
    assert config.sampling.normalized_rates() == (1, 10, 100)
    assert config.output.staged_dir.name == "staged"


def test_load_pipeline_config_rejects_invalid_timeout(tmp_path: Path) -> None:
    config_path = tmp_path / "invalid.yaml"
    config_path.write_text(
        """
dataset:
  dataset_id: invalid_trace
  input_dir: ../data/raw/invalid_trace

output:
  staged_dir: ../data/staged
  processed_dir: ../data/processed
  results_tables_dir: ../results/tables
  results_plots_dir: ../results/plots

methodology:
  inactivity_timeout_seconds: 0
""".strip()
        + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match="positive integer"):
        load_pipeline_config(config_path)

