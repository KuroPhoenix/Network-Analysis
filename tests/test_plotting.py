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
                "sampling_rate": 1,
                "sampling_method": "systematic",
                "random_seed": None,
                "baseline_flow_count": 5,
                "detected_flow_count": 5,
                "undetected_flow_count": 0,
                "flow_detection_rate": 1.0,
                "sampled_packet_count": 8,
                "sampled_flow_count": 5,
                "size_basis": "bytes",
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
                "size_basis": "bytes",
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
                "size_basis": "bytes",
                "byte_basis": "captured_len",
            },
        ]
    ).write_parquet(artifact_paths.metric_summary)

    pl.DataFrame(
        [
            {
                "dataset_id": "fixture_trace",
                "sampling_rate": 1,
                "sampling_method": "systematic",
                "random_seed": None,
                "flow_id": "flow-1",
                "detection_status": "detected",
                "size_basis": "packets",
                "byte_basis": "captured_len",
                "baseline_size": 100.0,
                "sampled_size_estimate": 100.0,
                "baseline_duration_seconds": 10.0,
                "sampled_duration_seconds": 10.0,
                "baseline_sending_rate": 10.0,
                "sampled_sending_rate": 10.0,
                "flow_size_overestimation_factor": 1.0,
                "flow_duration_underestimation_factor": 1.0,
                "flow_sending_rate_overestimation_factor": 1.0,
            },
            {
                "dataset_id": "fixture_trace",
                "sampling_rate": 1,
                "sampling_method": "systematic",
                "random_seed": None,
                "flow_id": "flow-2",
                "detection_status": "detected",
                "size_basis": "packets",
                "byte_basis": "captured_len",
                "baseline_size": 200.0,
                "sampled_size_estimate": 200.0,
                "baseline_duration_seconds": 20.0,
                "sampled_duration_seconds": 20.0,
                "baseline_sending_rate": 10.0,
                "sampled_sending_rate": 10.0,
                "flow_size_overestimation_factor": 1.0,
                "flow_duration_underestimation_factor": 1.0,
                "flow_sending_rate_overestimation_factor": 1.0,
            },
            {
                "dataset_id": "fixture_trace",
                "sampling_rate": 2,
                "sampling_method": "systematic",
                "random_seed": None,
                "flow_id": "flow-1",
                "detection_status": "detected",
                "size_basis": "packets",
                "byte_basis": "captured_len",
                "baseline_size": 100.0,
                "sampled_size_estimate": 120.0,
                "baseline_duration_seconds": 10.0,
                "sampled_duration_seconds": 8.0,
                "baseline_sending_rate": 10.0,
                "sampled_sending_rate": 15.0,
                "flow_size_overestimation_factor": 1.2,
                "flow_duration_underestimation_factor": 0.8,
                "flow_sending_rate_overestimation_factor": 1.5,
            },
            {
                "dataset_id": "fixture_trace",
                "sampling_rate": 2,
                "sampling_method": "systematic",
                "random_seed": None,
                "flow_id": "flow-2",
                "detection_status": "detected",
                "size_basis": "packets",
                "byte_basis": "captured_len",
                "baseline_size": 200.0,
                "sampled_size_estimate": 180.0,
                "baseline_duration_seconds": 20.0,
                "sampled_duration_seconds": 16.0,
                "baseline_sending_rate": 10.0,
                "sampled_sending_rate": 11.25,
                "flow_size_overestimation_factor": 0.9,
                "flow_duration_underestimation_factor": 0.8,
                "flow_sending_rate_overestimation_factor": 1.125,
            },
            {
                "dataset_id": "fixture_trace",
                "sampling_rate": 3,
                "sampling_method": "systematic",
                "random_seed": None,
                "flow_id": "flow-1",
                "detection_status": "detected",
                "size_basis": "packets",
                "byte_basis": "captured_len",
                "baseline_size": 100.0,
                "sampled_size_estimate": 150.0,
                "baseline_duration_seconds": 10.0,
                "sampled_duration_seconds": 6.0,
                "baseline_sending_rate": 10.0,
                "sampled_sending_rate": 25.0,
                "flow_size_overestimation_factor": 1.5,
                "flow_duration_underestimation_factor": 0.6,
                "flow_sending_rate_overestimation_factor": 2.5,
            },
            {
                "dataset_id": "fixture_trace",
                "sampling_rate": 3,
                "sampling_method": "systematic",
                "random_seed": None,
                "flow_id": "flow-2",
                "detection_status": "undetected",
                "size_basis": "packets",
                "byte_basis": "captured_len",
                "baseline_size": 200.0,
                "sampled_size_estimate": None,
                "baseline_duration_seconds": 20.0,
                "sampled_duration_seconds": None,
                "baseline_sending_rate": 10.0,
                "sampled_sending_rate": None,
                "flow_size_overestimation_factor": None,
                "flow_duration_underestimation_factor": None,
                "flow_sending_rate_overestimation_factor": None,
            },
            {
                "dataset_id": "fixture_trace",
                "sampling_rate": 1,
                "sampling_method": "systematic",
                "random_seed": None,
                "flow_id": "flow-1",
                "detection_status": "detected",
                "size_basis": "bytes",
                "byte_basis": "captured_len",
                "baseline_size": 1000.0,
                "sampled_size_estimate": 1000.0,
                "baseline_duration_seconds": 10.0,
                "sampled_duration_seconds": 10.0,
                "baseline_sending_rate": 100.0,
                "sampled_sending_rate": 100.0,
                "flow_size_overestimation_factor": 1.0,
                "flow_duration_underestimation_factor": 1.0,
                "flow_sending_rate_overestimation_factor": 1.0,
            },
            {
                "dataset_id": "fixture_trace",
                "sampling_rate": 1,
                "sampling_method": "systematic",
                "random_seed": None,
                "flow_id": "flow-2",
                "detection_status": "detected",
                "size_basis": "bytes",
                "byte_basis": "captured_len",
                "baseline_size": 2000.0,
                "sampled_size_estimate": 2000.0,
                "baseline_duration_seconds": 20.0,
                "sampled_duration_seconds": 20.0,
                "baseline_sending_rate": 100.0,
                "sampled_sending_rate": 100.0,
                "flow_size_overestimation_factor": 1.0,
                "flow_duration_underestimation_factor": 1.0,
                "flow_sending_rate_overestimation_factor": 1.0,
            },
            {
                "dataset_id": "fixture_trace",
                "sampling_rate": 2,
                "sampling_method": "systematic",
                "random_seed": None,
                "flow_id": "flow-1",
                "detection_status": "detected",
                "size_basis": "bytes",
                "byte_basis": "captured_len",
                "baseline_size": 1000.0,
                "sampled_size_estimate": 1300.0,
                "baseline_duration_seconds": 10.0,
                "sampled_duration_seconds": 8.0,
                "baseline_sending_rate": 100.0,
                "sampled_sending_rate": 162.5,
                "flow_size_overestimation_factor": 1.3,
                "flow_duration_underestimation_factor": 0.8,
                "flow_sending_rate_overestimation_factor": 1.625,
            },
            {
                "dataset_id": "fixture_trace",
                "sampling_rate": 2,
                "sampling_method": "systematic",
                "random_seed": None,
                "flow_id": "flow-2",
                "detection_status": "detected",
                "size_basis": "bytes",
                "byte_basis": "captured_len",
                "baseline_size": 2000.0,
                "sampled_size_estimate": 1800.0,
                "baseline_duration_seconds": 20.0,
                "sampled_duration_seconds": 16.0,
                "baseline_sending_rate": 100.0,
                "sampled_sending_rate": 112.5,
                "flow_size_overestimation_factor": 0.9,
                "flow_duration_underestimation_factor": 0.8,
                "flow_sending_rate_overestimation_factor": 1.125,
            },
            {
                "dataset_id": "fixture_trace",
                "sampling_rate": 3,
                "sampling_method": "systematic",
                "random_seed": None,
                "flow_id": "flow-1",
                "detection_status": "detected",
                "size_basis": "bytes",
                "byte_basis": "captured_len",
                "baseline_size": 1000.0,
                "sampled_size_estimate": 1600.0,
                "baseline_duration_seconds": 10.0,
                "sampled_duration_seconds": 6.0,
                "baseline_sending_rate": 100.0,
                "sampled_sending_rate": 266.67,
                "flow_size_overestimation_factor": 1.6,
                "flow_duration_underestimation_factor": 0.6,
                "flow_sending_rate_overestimation_factor": 2.6667,
            },
            {
                "dataset_id": "fixture_trace",
                "sampling_rate": 3,
                "sampling_method": "systematic",
                "random_seed": None,
                "flow_id": "flow-2",
                "detection_status": "undetected",
                "size_basis": "bytes",
                "byte_basis": "captured_len",
                "baseline_size": 2000.0,
                "sampled_size_estimate": None,
                "baseline_duration_seconds": 20.0,
                "sampled_duration_seconds": None,
                "baseline_sending_rate": 100.0,
                "sampled_sending_rate": None,
                "flow_size_overestimation_factor": None,
                "flow_duration_underestimation_factor": None,
                "flow_sending_rate_overestimation_factor": None,
            },
        ]
    ).write_parquet(artifact_paths.flow_metrics)

    plots_dir = plotting.run_module(config)
    assert plots_dir.exists()
    assert plots_dir == artifact_paths.plots_dir

    expected_files = {
        "fixture_trace_flow_detection_rate.svg",
        "fixture_trace_flow_packet_size_estimation.svg",
        "fixture_trace_flow_byte_size_estimation.svg",
        "fixture_trace_flow_duration_estimation.svg",
        "fixture_trace_flow_packet_sending_rate.svg",
        "fixture_trace_flow_byte_sending_rate.svg",
        "fixture_trace_flow_packet_size_overestimation_factor_cdf.svg",
        "fixture_trace_flow_byte_size_overestimation_factor_cdf.svg",
        "fixture_trace_flow_duration_underestimation_factor_cdf.svg",
        "fixture_trace_flow_packet_sending_rate_overestimation_factor_cdf.svg",
        "fixture_trace_flow_byte_sending_rate_overestimation_factor_cdf.svg",
        "fixture_trace_plotting_summary.parquet",
    }
    assert {path.name for path in plots_dir.iterdir()} == expected_files

    detection_svg = (plots_dir / "fixture_trace_flow_detection_rate.svg").read_text(encoding="utf-8")
    packet_size_svg = (plots_dir / "fixture_trace_flow_packet_size_estimation.svg").read_text(encoding="utf-8")
    packet_factor_svg = (
        plots_dir / "fixture_trace_flow_packet_size_overestimation_factor_cdf.svg"
    ).read_text(encoding="utf-8")
    plotting_summary = pl.read_parquet(plots_dir / "fixture_trace_plotting_summary.parquet")

    assert "Flow detection rate vs sampling rate" in detection_svg
    assert "ground truth baseline" in detection_svg
    assert "1:1" in detection_svg
    assert "1:2" in detection_svg
    assert "1:3" in detection_svg
    assert "Flow packet size estimation vs sampling rate" in packet_size_svg
    assert "median over detected flows" in packet_size_svg
    assert "Flow packet size overestimation factor CDF" in packet_factor_svg
    assert "Empirical CDF" in packet_factor_svg
    assert set(plotting_summary["plot_key"]) == {
        "flow_detection_rate",
        "flow_packet_size_estimation",
        "flow_byte_size_estimation",
        "flow_duration_estimation",
        "flow_packet_sending_rate",
        "flow_byte_sending_rate",
    }


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
