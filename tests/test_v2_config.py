"""Tests for the active-architecture config scaffolding."""

from pathlib import Path

import dpkt

from network_analysis.shared.types import CachePolicy, SizeBasis
from network_analysis.shared.v2_config import (
    load_dataset_template,
    load_run_config,
    resolve_dataset_runs,
)


def test_load_run_config_applies_defaults_and_preserves_methodology(tmp_path: Path) -> None:
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

    assert config.paths.datasets_root == (tmp_path / "datasets").resolve()
    assert config.paths.results_root == (tmp_path / "results").resolve()
    assert config.methodology.inactivity_timeout_seconds == 15
    assert config.methodology.size_basis == SizeBasis.PACKETS
    assert config.sampling.normalized_rates() == (1, 10, 100)
    assert config.runtime.cache_policy == CachePolicy.MINIMAL
    assert config.runtime.plotting_mode == "minimal"
    assert config.runtime.logging.level == "INFO"


def test_resolve_dataset_runs_discovers_dataset_scoped_outputs(tmp_path: Path) -> None:
    datasets_root = tmp_path / "datasets"
    bras_dir = datasets_root / "bras"
    onu_dir = datasets_root / "onu"
    bras_dir.mkdir(parents=True)
    onu_dir.mkdir(parents=True)

    _write_empty_pcap_capture(bras_dir / "capture_1.pcap")
    _write_empty_pcap_capture(bras_dir / "capture_2.pcapng")
    _write_empty_pcap_capture(onu_dir / "capture_1.pcap")
    (onu_dir / "notes.txt").write_text("ignore me\n", encoding="utf-8")

    dataset_template_path = tmp_path / "dataset_template.yaml"
    dataset_template_path.write_text(
        """
discovery:
  dataset_glob: "*"
  raw_glob: "*.pcap*"
""".strip()
        + "\n",
        encoding="utf-8",
    )
    run_config_path = tmp_path / "run_conf.yaml"
    run_config_path.write_text(
        """
input:
  datasets_root: ./datasets

output:
  results_root: ./results

sampling:
  rates:
    - 2
  method: systematic
""".strip()
        + "\n",
        encoding="utf-8",
    )

    dataset_template = load_dataset_template(dataset_template_path)
    run_config = load_run_config(run_config_path)
    resolved_runs = resolve_dataset_runs(run_config, dataset_template)

    assert [(run.dataset_id, len(run.capture_files)) for run in resolved_runs] == [
        ("bras", 2),
        ("onu", 1),
    ]
    assert resolved_runs[0].meta_dir == (tmp_path / "results" / "bras" / "meta").resolve()
    assert resolved_runs[0].tables_dir == (tmp_path / "results" / "bras" / "tables").resolve()
    assert resolved_runs[0].plots_dir == (tmp_path / "results" / "bras" / "plots").resolve()
    assert resolved_runs[0].logs_dir == (tmp_path / "results" / "bras" / "logs").resolve()


def _write_empty_pcap_capture(path: Path) -> None:
    with path.open("wb") as handle:
        writer = dpkt.pcap.Writer(handle)
        writer.close()
