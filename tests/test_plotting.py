"""Tests for the lightweight plotting module."""

from __future__ import annotations

from pathlib import Path

import polars as pl

from network_analysis.modules import plotting
from network_analysis.shared.artifacts import build_artifact_paths
from network_analysis.shared.config import load_pipeline_config


def test_plotting_renders_detection_rate_svg_from_metric_summary(tmp_path: Path) -> None:
    config_path = _write_config(tmp_path)
    config = load_pipeline_config(config_path)
    artifact_paths = build_artifact_paths(config)
    artifact_paths.results_tables_dir.mkdir(parents=True, exist_ok=True)

    pl.DataFrame(
        [
            {
                "dataset_id": "fixture_trace",
                "sampling_rate": 1,
                "sampling_method": "systematic",
                "random_seed": None,
                "baseline_flow_count": 5,
                "detected_flow_count": 5,
                "undetected_flow_count": 0,
                "flow_detection_rate": 1.0,
                "sampled_packet_count": 8,
                "sampled_flow_count": 5,
                "size_basis": "packets",
                "byte_basis": "captured_len",
            },
            {
                "dataset_id": "fixture_trace",
                "sampling_rate": 2,
                "sampling_method": "systematic",
                "random_seed": None,
                "baseline_flow_count": 5,
                "detected_flow_count": 3,
                "undetected_flow_count": 2,
                "flow_detection_rate": 0.6,
                "sampled_packet_count": 4,
                "sampled_flow_count": 3,
                "size_basis": "packets",
                "byte_basis": "captured_len",
            },
            {
                "dataset_id": "fixture_trace",
                "sampling_rate": 3,
                "sampling_method": "systematic",
                "random_seed": None,
                "baseline_flow_count": 5,
                "detected_flow_count": 3,
                "undetected_flow_count": 2,
                "flow_detection_rate": 0.6,
                "sampled_packet_count": 3,
                "sampled_flow_count": 3,
                "size_basis": "packets",
                "byte_basis": "captured_len",
            },
        ]
    ).write_parquet(artifact_paths.metric_summary)

    plot_path = plotting.run_module(config)
    assert plot_path.exists()
    assert plot_path.name == "fixture_trace_flow_detection_rate.svg"

    svg_text = plot_path.read_text(encoding="utf-8")
    assert "Flow detection rate vs sampling rate" in svg_text
    assert "ground truth baseline" in svg_text
    assert "Dataset fixture_trace" in svg_text
    assert "1:1" in svg_text
    assert "1:2" in svg_text
    assert "1:3" in svg_text
    assert "1.00" in svg_text
    assert "0.60" in svg_text


def _write_config(tmp_path: Path) -> Path:
    config_path = tmp_path / "pipeline.yaml"
    config_path.write_text(
        f"""
dataset:
  dataset_id: fixture_trace
  input_dir: {tmp_path / "raw"}
  raw_glob: "*.pcap"

output:
  staged_dir: {tmp_path / "staged"}
  processed_dir: {tmp_path / "processed"}
  results_tables_dir: {tmp_path / "tables"}
  results_plots_dir: {tmp_path / "plots"}

methodology:
  flow_key_fields:
    - src_ip
    - dst_ip
    - src_port
    - dst_port
    - protocol
  inactivity_timeout_seconds: 15
  size_basis: packets
  byte_basis: captured_len

sampling:
  rates:
    - 2
    - 3
  method: systematic

runtime:
  workers: 1
  enable_plots: true
""".strip()
        + "\n",
        encoding="utf-8",
    )
    return config_path
