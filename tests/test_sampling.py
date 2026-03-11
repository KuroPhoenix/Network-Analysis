"""Tests for deterministic packet sampling and sampled-flow reconstruction."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import polars as pl

from network_analysis import flow_construction, sampling
from network_analysis.artifacts import build_artifact_paths

from tests.support import build_dataset_run_config


def test_sampling_reconstructs_sampled_flows_from_sampled_packets_only(tmp_path: Path) -> None:
    config = build_dataset_run_config(tmp_path, raw_glob="*.pcap", sampling_rates=(2, 3), plotting_mode="off")
    artifact_paths = build_artifact_paths(config)
    artifact_paths.processed_dir.mkdir(parents=True, exist_ok=True)

    pl.DataFrame(_packet_rows()).write_parquet(artifact_paths.packets)
    flow_construction.run_module(config)

    sampled_packets_dir, sampled_flows_dir, sampling_manifest_path = sampling.run_module(config)
    assert sampled_packets_dir == artifact_paths.sampled_packets_dir
    assert sampled_flows_dir == artifact_paths.sampled_flows_dir
    assert sampling_manifest_path == artifact_paths.sampling_manifest

    sampling_manifest = pl.read_parquet(sampling_manifest_path).sort("sampling_rate")
    assert sampling_manifest["sampling_rate"].to_list() == [1, 2, 3]
    assert sampling_manifest["sampled_packet_count"].to_list() == [4, 2, 2]
    assert sampling_manifest["sampled_flow_count"].to_list() == [2, 2, 2]

    rate_two_packets = pl.read_parquet(Path(sampling_manifest.filter(pl.col("sampling_rate") == 2).item(0, "sampled_packets_path")))
    assert rate_two_packets["packet_index"].to_list() == [1, 3]

    rate_two_flows = pl.read_parquet(Path(sampling_manifest.filter(pl.col("sampling_rate") == 2).item(0, "sampled_flows_path"))).sort(
        "sampled_flow_id"
    )
    assert rate_two_flows["protocol"].to_list() == ["tcp", "tcp"]
    assert rate_two_flows["flow_sequence"].to_list() == [1, 2]
    assert rate_two_flows["sampled_packet_count"].to_list() == [1, 1]
    assert rate_two_flows["estimated_packet_count"].to_list() == [2, 2]
    assert rate_two_flows["duration_seconds"].to_list() == [0.0, 0.0]

    rate_three_packets = pl.read_parquet(Path(sampling_manifest.filter(pl.col("sampling_rate") == 3).item(0, "sampled_packets_path")))
    assert rate_three_packets["packet_index"].to_list() == [1, 4]


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
