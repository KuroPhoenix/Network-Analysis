"""End-to-end validation for the active per-dataset execution config."""

from __future__ import annotations

from pathlib import Path
import socket

import dpkt
import polars as pl

from network_analysis.artifacts import build_artifact_paths
from network_analysis.driver import ModuleRuntimeEvent, run_pipeline

from tests.support import build_dataset_run_config


def test_run_pipeline_executes_end_to_end_pipeline_without_plots(tmp_path: Path) -> None:
    raw_dir = tmp_path / "datasets" / "fixture_trace"
    raw_dir.mkdir(parents=True)
    capture_path = raw_dir / "fixture_trace.pcap"
    _write_fixture_pcap(capture_path)

    config = build_dataset_run_config(tmp_path, raw_glob="*.pcap", sampling_rates=(2, 3), plotting_mode="off")
    run_pipeline(config)
    artifact_paths = build_artifact_paths(config)
    assert artifact_paths.dataset_registry.exists()
    assert artifact_paths.ingest_manifest.exists()
    assert artifact_paths.packets.exists()
    assert artifact_paths.baseline_flows.exists()
    assert artifact_paths.sampling_manifest.exists()
    assert artifact_paths.metric_summary.exists()
    assert artifact_paths.flow_metrics.exists()
    assert not artifact_paths.plots_dir.exists()

    summary_frame = pl.read_parquet(artifact_paths.metric_summary).sort(["sampling_rate", "size_basis"])
    assert summary_frame["sampling_rate"].to_list() == [1, 2, 3]
    assert summary_frame["flow_detection_rate"].to_list() == [1.0, 0.5, 1.0]


def test_run_pipeline_emits_runtime_events_for_each_module(tmp_path: Path) -> None:
    raw_dir = tmp_path / "datasets" / "fixture_trace"
    raw_dir.mkdir(parents=True)
    capture_path = raw_dir / "fixture_trace.pcap"
    _write_fixture_pcap(capture_path)

    config = build_dataset_run_config(tmp_path, raw_glob="*.pcap", sampling_rates=(2, 3), plotting_mode="off")
    events: list[ModuleRuntimeEvent] = []

    run_pipeline(config, observer=events.append)

    assert [event.status for event in events].count("starting") == 6
    assert [event.status for event in events].count("completed") == 6
    assert all(event.status != "failed" for event in events)
    assert [event.module_name for event in events if event.status == "starting"] == [
        "dataset_registry",
        "ingest",
        "packet_extraction",
        "flow_construction",
        "sampling",
        "metrics",
    ]
    assert {event.module_total for event in events} == {6}
    assert all(event.dataset_id == "fixture_trace" for event in events)
    assert all(
        event.elapsed_seconds is None if event.status == "starting" else event.elapsed_seconds is not None
        for event in events
    )


def _write_fixture_pcap(path: Path) -> None:
    base_time = 1_700_000_000.0
    packets = [
        _build_tcp_frame("10.0.0.1", "10.0.0.2", 12345, 80, b"flow-a-1"),
        _build_tcp_frame("10.0.0.1", "10.0.0.2", 12345, 80, b"flow-a-2"),
        _build_tcp_frame("10.0.0.1", "10.0.0.2", 12345, 80, b"flow-a-3"),
        _build_udp_frame("10.0.0.3", "10.0.0.4", 5353, 53, b"flow-b-1"),
    ]

    with path.open("wb") as handle:
        writer = dpkt.pcap.Writer(handle)
        writer.writepkt(packets[0], ts=base_time)
        writer.writepkt(packets[1], ts=base_time + 10)
        writer.writepkt(packets[2], ts=base_time + 20)
        writer.writepkt(packets[3], ts=base_time + 25)
        writer.close()


def _build_tcp_frame(src_ip: str, dst_ip: str, src_port: int, dst_port: int, payload: bytes) -> bytes:
    tcp = dpkt.tcp.TCP(sport=src_port, dport=dst_port, seq=1, flags=dpkt.tcp.TH_ACK, data=payload)
    tcp.off = 5
    ip = dpkt.ip.IP(
        src=socket.inet_aton(src_ip),
        dst=socket.inet_aton(dst_ip),
        p=dpkt.ip.IP_PROTO_TCP,
        ttl=64,
        data=tcp,
    )
    ip.len = len(ip)
    ethernet = dpkt.ethernet.Ethernet(
        src=b"\xaa\xaa\xaa\xaa\xaa\xaa",
        dst=b"\xbb\xbb\xbb\xbb\xbb\xbb",
        type=dpkt.ethernet.ETH_TYPE_IP,
        data=ip,
    )
    return bytes(ethernet)


def _build_udp_frame(src_ip: str, dst_ip: str, src_port: int, dst_port: int, payload: bytes) -> bytes:
    udp = dpkt.udp.UDP(sport=src_port, dport=dst_port, data=payload)
    udp.ulen = len(udp)
    ip = dpkt.ip.IP(
        src=socket.inet_aton(src_ip),
        dst=socket.inet_aton(dst_ip),
        p=dpkt.ip.IP_PROTO_UDP,
        ttl=64,
        data=udp,
    )
    ip.len = len(ip)
    ethernet = dpkt.ethernet.Ethernet(
        src=b"\xaa\xaa\xaa\xaa\xaa\xaa",
        dst=b"\xbb\xbb\xbb\xbb\xbb\xbb",
        type=dpkt.ethernet.ETH_TYPE_IP,
        data=ip,
    )
    return bytes(ethernet)
