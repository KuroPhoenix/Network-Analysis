"""Tests for the active dataset-root runtime layer."""

from pathlib import Path

import dpkt

from network_analysis.runtime import plan_active_runs
from network_analysis.shared.v2_config import load_dataset_template, load_run_config


def test_plan_active_runs_adapts_dataset_scoped_results(tmp_path: Path) -> None:
    datasets_root = tmp_path / "datasets"
    bras_dir = datasets_root / "bras"
    onu_dir = datasets_root / "onu"
    bras_dir.mkdir(parents=True)
    onu_dir.mkdir(parents=True)

    _write_empty_pcap_capture(bras_dir / "capture_1.pcap")
    _write_empty_pcap_capture(onu_dir / "capture_1.pcapng")

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

runtime:
  plotting_mode: off
""".strip()
        + "\n",
        encoding="utf-8",
    )

    planned_runs = plan_active_runs(
        load_run_config(run_config_path),
        load_dataset_template(dataset_template_path),
    )

    assert [planned_run.resolved_run.dataset_id for planned_run in planned_runs] == ["bras", "onu"]
    assert planned_runs[0].pipeline_config.output.results_tables_dir == (
        tmp_path / "results" / "bras" / "tables"
    ).resolve()
    assert planned_runs[0].pipeline_config.output.staged_dir == (
        tmp_path / "data" / "staged"
    ).resolve()
    assert planned_runs[0].pipeline_config.runtime.enable_plots is False


def _write_empty_pcap_capture(path: Path) -> None:
    with path.open("wb") as handle:
        writer = dpkt.pcap.Writer(handle)
        writer.close()
