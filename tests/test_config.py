"""Tests for the active config loader."""

from pathlib import Path

import pytest

from network_analysis.config import ConfigError, load_run_config
from network_analysis.constants import (
    DEFAULT_FLOW_KEY_FIELDS,
    DEFAULT_INACTIVITY_TIMEOUT_SECONDS,
)
from network_analysis.types import SizeBasis


def test_load_run_config_applies_defaults_and_adds_baseline(tmp_path: Path) -> None:
    config_path = tmp_path / "run_conf.yaml"
    config_path.write_text(
        """
input:
  datasets_root: ./datasets

output:
  results_root: ./results

sampling:
  rates:
    - 10
    - 100
  method: systematic
""".strip()
        + "\n",
        encoding="utf-8",
    )

    config = load_run_config(config_path)

    assert config.methodology.flow_key_fields == DEFAULT_FLOW_KEY_FIELDS
    assert config.methodology.inactivity_timeout_seconds == DEFAULT_INACTIVITY_TIMEOUT_SECONDS
    assert config.methodology.size_basis == SizeBasis.PACKETS
    assert config.sampling.normalized_rates() == (1, 10, 100)
    assert config.paths.datasets_root == (tmp_path / "datasets").resolve()
    assert config.paths.results_root == (tmp_path / "results").resolve()


def test_load_run_config_rejects_invalid_timeout(tmp_path: Path) -> None:
    config_path = tmp_path / "run_conf.yaml"
    config_path.write_text(
        """
input:
  datasets_root: ./datasets

output:
  results_root: ./results

methodology:
  inactivity_timeout_seconds: 0
""".strip()
        + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match="positive integer"):
        load_run_config(config_path)
