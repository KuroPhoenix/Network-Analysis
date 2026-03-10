"""Tests for baseline flow construction."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import polars as pl
import pytest

from network_analysis.modules import flow_construction
from network_analysis.shared.artifacts import build_artifact_paths
from network_analysis.shared.config import load_pipeline_config


def test_flow_construction_respects_timeout_boundary_and_zero_duration_flows(tmp_path: Path) -> None:
    config_path = _write_config(tmp_path)
    config = load_pipeline_config(config_path)
    artifact_paths = build_artifact_paths(config)
    artifact_paths.processed_dir.mkdir(parents=True, exist_ok=True)

    packets = pl.DataFrame(_packet_rows())
    packets.write_parquet(artifact_paths.packets)

    baseline_flow_path = flow_construction.run_module(config)
    assert baseline_flow_path == artifact_paths.baseline_flows
    assert baseline_flow_path.exists()

    flow_frame = pl.read_parquet(baseline_flow_path)
    assert flow_frame.columns == [
        "dataset_id",
        "flow_id",
        "src_ip",
        "dst_ip",
        "src_port",
        "dst_port",
        "protocol",
        "flow_sequence",
        "start_ts",
        "end_ts",
        "start_packet_index",
        "end_packet_index",
        "duration_seconds",
        "packet_count",
        "byte_count",
        "sending_rate_packets_per_second",
        "sending_rate_bytes_per_second",
        "size_basis",
        "byte_basis",
    ]

    rows = flow_frame.sort("flow_id").to_dicts()
    assert len(rows) == 3

    first_flow = rows[0]
    assert first_flow["flow_id"] == "fixture_trace-flow-000001"
    assert first_flow["flow_sequence"] == 1
    assert first_flow["src_ip"] == "10.0.0.1"
    assert first_flow["dst_ip"] == "10.0.0.2"
    assert first_flow["src_port"] == 12345
    assert first_flow["dst_port"] == 80
    assert first_flow["protocol"] == "tcp"
    assert first_flow["start_packet_index"] == 1
    assert first_flow["end_packet_index"] == 3
    assert first_flow["duration_seconds"] == pytest.approx(15.0)
    assert first_flow["packet_count"] == 2
    assert first_flow["byte_count"] == 210
    assert first_flow["sending_rate_packets_per_second"] == pytest.approx(2 / 15)
    assert first_flow["sending_rate_bytes_per_second"] == pytest.approx(14.0)
    assert first_flow["size_basis"] == "packets"
    assert first_flow["byte_basis"] == "captured_len"

    second_flow = rows[1]
    assert second_flow["flow_id"] == "fixture_trace-flow-000002"
    assert second_flow["flow_sequence"] == 1
    assert second_flow["src_ip"] == "10.0.0.3"
    assert second_flow["dst_ip"] == "10.0.0.4"
    assert second_flow["protocol"] == "udp"
    assert second_flow["duration_seconds"] == pytest.approx(0.0)
    assert second_flow["packet_count"] == 1
    assert second_flow["byte_count"] == 200
    assert second_flow["sending_rate_packets_per_second"] is None
    assert second_flow["sending_rate_bytes_per_second"] is None

    third_flow = rows[2]
    assert third_flow["flow_id"] == "fixture_trace-flow-000003"
    assert third_flow["flow_sequence"] == 2
    assert third_flow["src_ip"] == "10.0.0.1"
    assert third_flow["dst_ip"] == "10.0.0.2"
    assert third_flow["protocol"] == "tcp"
    assert third_flow["duration_seconds"] == pytest.approx(0.0)
    assert third_flow["packet_count"] == 1
    assert third_flow["byte_count"] == 120
    assert third_flow["sending_rate_packets_per_second"] is None
    assert third_flow["sending_rate_bytes_per_second"] is None


def _packet_rows() -> list[dict[str, object]]:
    base_ts = datetime(2024, 1, 1, 0, 0, 0)
    return [
        {
            "dataset_id": "fixture_trace",
            "source_discovery_index": 1,
            "source_member_index": 1,
            "source_file": "fixture.pcap",
            "packet_index": 1,
            "source_packet_index": 1,
            "timestamp_us": 1_704_067_200_000_000,
            "timestamp": base_ts,
            "captured_len": 100,
            "wire_len": None,
            "protocol": "tcp",
            "src_ip": "10.0.0.1",
            "dst_ip": "10.0.0.2",
            "src_port": 12345,
            "dst_port": 80,
            "tcp_flags": "16",
            "flow_eligible": True,
            "flow_ineligible_reason": None,
        },
        {
            "dataset_id": "fixture_trace",
            "source_discovery_index": 1,
            "source_member_index": 1,
            "source_file": "fixture.pcap",
            "packet_index": 2,
            "source_packet_index": 2,
            "timestamp_us": 1_704_067_205_000_000,
            "timestamp": base_ts + timedelta(seconds=5),
            "captured_len": 200,
            "wire_len": None,
            "protocol": "udp",
            "src_ip": "10.0.0.3",
            "dst_ip": "10.0.0.4",
            "src_port": 5353,
            "dst_port": 53,
            "tcp_flags": None,
            "flow_eligible": True,
            "flow_ineligible_reason": None,
        },
        {
            "dataset_id": "fixture_trace",
            "source_discovery_index": 1,
            "source_member_index": 1,
            "source_file": "fixture.pcap",
            "packet_index": 3,
            "source_packet_index": 3,
            "timestamp_us": 1_704_067_215_000_000,
            "timestamp": base_ts + timedelta(seconds=15),
            "captured_len": 110,
            "wire_len": None,
            "protocol": "tcp",
            "src_ip": "10.0.0.1",
            "dst_ip": "10.0.0.2",
            "src_port": 12345,
            "dst_port": 80,
            "tcp_flags": "16",
            "flow_eligible": True,
            "flow_ineligible_reason": None,
        },
        {
            "dataset_id": "fixture_trace",
            "source_discovery_index": 1,
            "source_member_index": 1,
            "source_file": "fixture.pcap",
            "packet_index": 4,
            "source_packet_index": 4,
            "timestamp_us": 1_704_067_231_000_000,
            "timestamp": base_ts + timedelta(seconds=31),
            "captured_len": 120,
            "wire_len": None,
            "protocol": "tcp",
            "src_ip": "10.0.0.1",
            "dst_ip": "10.0.0.2",
            "src_port": 12345,
            "dst_port": 80,
            "tcp_flags": "16",
            "flow_eligible": True,
            "flow_ineligible_reason": None,
        },
    ]


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
  method: systematic

runtime:
  workers: 1
  enable_plots: false
""".strip()
        + "\n",
        encoding="utf-8",
    )
    return config_path
