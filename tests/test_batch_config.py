"""Tests for the batch-runner config loader."""

from pathlib import Path

import pytest

from network_analysis.shared.batch_config import BatchConfigError, load_batch_config


def test_load_batch_config_applies_defaults(sample_batch_config_path: Path) -> None:
    config = load_batch_config(sample_batch_config_path)

    assert config.discovery.dataset_glob == "*"
    assert config.sampling.normalized_rates() == (1, 2, 5)
    assert config.runtime.enable_plots is True


def test_load_batch_config_rejects_missing_datasets_root(tmp_path: Path) -> None:
    config_path = tmp_path / "invalid-batch.yaml"
    config_path.write_text(
        """
discovery:
  datasets_root: ""

output:
  staged_root: ../data/staged
  processed_root: ../data/processed
  results_root: ../results
""".strip()
        + "\n",
        encoding="utf-8",
    )

    with pytest.raises(BatchConfigError, match="non-empty string"):
        load_batch_config(config_path)
