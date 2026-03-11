"""Tests for baseline-vs-sampled metric computation."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import polars as pl
import pytest

from network_analysis import flow_construction, metrics, sampling
from network_analysis.artifacts import build_artifact_paths

from tests.support import build_dataset_run_config


def test_metrics_keep_baseline_denominator_and_handle_zero_duration_cases(tmp_path: Path) -> None:
    config = build_dataset_run_config(tmp_path, raw_glob="*.pcap", sampling_rates=(2, 3), plotting_mode="off")
    artifact_paths = build_artifact_paths(config)
    artifact_paths.processed_dir.mkdir(parents=True, exist_ok=True)

    pl.DataFrame(_packet_rows()).write_parquet(artifact_paths.packets)
    flow_construction.run_module(config)
    sampling.run_module(config)

    metric_summary_path, flow_metrics_path = metrics.run_module(config)
    assert metric_summary_path == artifact_paths.metric_summary
    assert flow_metrics_path == artifact_paths.flow_metrics

    summary_frame = pl.read_parquet(metric_summary_path).sort(["sampling_rate", "size_basis"])
    assert summary_frame["sampling_rate"].to_list() == [1, 2, 3]
    assert summary_frame["baseline_flow_count"].to_list() == [2, 2, 2]
    assert summary_frame["detected_flow_count"].to_list() == [2, 1, 2]
    assert summary_frame["undetected_flow_count"].to_list() == [0, 1, 0]
    assert summary_frame["flow_detection_rate"].to_list() == [1.0, 0.5, 1.0]

    flow_metrics_frame = pl.read_parquet(flow_metrics_path)

    rate_two_flow_a = flow_metrics_frame.filter(
        (pl.col("sampling_rate") == 2) & (pl.col("flow_id") == "fixture_trace-flow-000001")
    ).row(0, named=True)
    assert rate_two_flow_a["detection_status"] == "detected"
    assert rate_two_flow_a["baseline_size"] == pytest.approx(3.0)
    assert rate_two_flow_a["sampled_size_estimate"] == pytest.approx(4.0)
    assert rate_two_flow_a["baseline_duration_seconds"] == pytest.approx(20.0)
    assert rate_two_flow_a["sampled_duration_seconds"] == pytest.approx(20.0)
    assert rate_two_flow_a["flow_size_overestimation_factor"] == pytest.approx(4 / 3)
    assert rate_two_flow_a["flow_duration_underestimation_factor"] == pytest.approx(1.0)
    assert rate_two_flow_a["flow_sending_rate_overestimation_factor"] == pytest.approx(4 / 3)

    rate_two_flow_b = flow_metrics_frame.filter(
        (pl.col("sampling_rate") == 2) & (pl.col("flow_id") == "fixture_trace-flow-000002")
    ).row(0, named=True)
    assert rate_two_flow_b["detection_status"] == "undetected"
    assert rate_two_flow_b["sampled_size_estimate"] is None
    assert rate_two_flow_b["sampled_duration_seconds"] is None
    assert rate_two_flow_b["flow_size_overestimation_factor"] is None

    rate_three_flow_a = flow_metrics_frame.filter(
        (pl.col("sampling_rate") == 3) & (pl.col("flow_id") == "fixture_trace-flow-000001")
    ).row(0, named=True)
    assert rate_three_flow_a["detection_status"] == "detected"
    assert rate_three_flow_a["sampled_duration_seconds"] == pytest.approx(0.0)
    assert rate_three_flow_a["flow_size_overestimation_factor"] == pytest.approx(1.0)
    assert rate_three_flow_a["flow_duration_underestimation_factor"] == pytest.approx(0.0)
    assert rate_three_flow_a["flow_sending_rate_overestimation_factor"] is None


def _packet_rows() -> list[dict[str, object]]:
    base_ts = datetime(2024, 1, 1, 0, 0, 0)
    return [
        _packet_row(
            packet_index=1,
            timestamp=base_ts,
            timestamp_us=1_704_067_200_000_000,
            captured_len=100,
            src_ip="10.0.0.1",
            dst_ip="10.0.0.2",
            src_port=12345,
            dst_port=80,
            protocol="tcp",
        ),
        _packet_row(
            packet_index=2,
            timestamp=base_ts + timedelta(seconds=10),
            timestamp_us=1_704_067_210_000_000,
            captured_len=110,
            src_ip="10.0.0.1",
            dst_ip="10.0.0.2",
            src_port=12345,
            dst_port=80,
            protocol="tcp",
        ),
        _packet_row(
            packet_index=3,
            timestamp=base_ts + timedelta(seconds=20),
            timestamp_us=1_704_067_220_000_000,
            captured_len=120,
            src_ip="10.0.0.1",
            dst_ip="10.0.0.2",
            src_port=12345,
            dst_port=80,
            protocol="tcp",
        ),
        _packet_row(
            packet_index=4,
            timestamp=base_ts + timedelta(seconds=25),
            timestamp_us=1_704_067_225_000_000,
            captured_len=130,
            src_ip="10.0.0.3",
            dst_ip="10.0.0.4",
            src_port=5353,
            dst_port=53,
            protocol="udp",
        ),
    ]


def _packet_row(
    *,
    packet_index: int,
    timestamp: datetime,
    timestamp_us: int,
    captured_len: int,
    src_ip: str,
    dst_ip: str,
    src_port: int,
    dst_port: int,
    protocol: str,
) -> dict[str, object]:
    return {
        "dataset_id": "fixture_trace",
        "source_discovery_index": 1,
        "source_member_index": 1,
        "source_file": "fixture.pcap",
        "packet_index": packet_index,
        "source_packet_index": packet_index,
        "timestamp_us": timestamp_us,
        "timestamp": timestamp,
        "captured_len": captured_len,
        "wire_len": None,
        "protocol": protocol,
        "src_ip": src_ip,
        "dst_ip": dst_ip,
        "src_port": src_port,
        "dst_port": dst_port,
        "tcp_flags": "16" if protocol == "tcp" else None,
        "flow_eligible": True,
        "flow_ineligible_reason": None,
    }
