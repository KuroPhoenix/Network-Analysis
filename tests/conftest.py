"""Shared test fixtures for the current MVP skeleton."""

from pathlib import Path
import sys

import dpkt
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


@pytest.fixture()
def sample_batch_config_path(tmp_path: Path) -> Path:
    """Create a minimal valid batch config and dataset tree."""

    datasets_root = tmp_path / "datasets"
    bras_dir = datasets_root / "Anonymized_bras_dataset"
    onu_dir = datasets_root / "Anonymized_onu_dataset"
    bras_dir.mkdir(parents=True)
    onu_dir.mkdir(parents=True)

    _write_empty_pcap_capture(bras_dir / "BRAS_capture_game_1.pcap")
    _write_empty_pcap_capture(bras_dir / "BRAS_capture_video_2.pcap")
    _write_empty_pcap_capture(onu_dir / "misc_trace.pcapng")
    (onu_dir / "notes.txt").write_text("ignore me\n", encoding="utf-8")

    config_path = tmp_path / "batch.yaml"
    config_path.write_text(
        """
discovery:
  datasets_root: ./datasets

output:
  staged_root: ./data/staged
  processed_root: ./data/processed
  results_root: ./results

sampling:
  rates:
    - 2
    - 5
  method: systematic

runtime:
  enable_plots: true
""".strip()
        + "\n",
        encoding="utf-8",
    )
    return config_path


def _write_empty_pcap_capture(path: Path) -> None:
    with path.open("wb") as handle:
        writer = dpkt.pcap.Writer(handle)
        writer.close()
