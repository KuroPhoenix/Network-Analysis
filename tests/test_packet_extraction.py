"""Tests for dataset registry, ingest, and packet extraction."""

from __future__ import annotations

from pathlib import Path
import socket

import dpkt
import polars as pl

from network_analysis.modules import dataset_registry, ingest, packet_extraction
from network_analysis.shared.config import load_pipeline_config


def test_packet_extraction_slice_preserves_raw_input_and_packet_order(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    capture_path = raw_dir / "fixture_trace.pcap"
    _write_fixture_pcap(capture_path)
    original_bytes = capture_path.read_bytes()

    config_path = _write_config(tmp_path, raw_dir)
    config = load_pipeline_config(config_path)

    registry_path = dataset_registry.run_module(config)
    ingest_manifest_path = ingest.run_module(config)
    packet_table_path, extraction_manifest_path = packet_extraction.run_module(config)

    registry_frame = pl.read_parquet(registry_path)
    assert registry_frame.height == 1
    assert registry_frame.item(0, "compression_type") == "none"
    assert registry_frame.item(0, "capture_format_hint") == "pcap"

    ingest_manifest = pl.read_parquet(ingest_manifest_path)
    staged_path = Path(ingest_manifest.item(0, "staged_file"))
    assert staged_path.exists()
    assert staged_path != capture_path
    assert capture_path.read_bytes() == original_bytes

    packet_frame = pl.read_parquet(packet_table_path)
    assert packet_frame.columns == [
        "dataset_id",
        "source_file",
        "packet_index",
        "source_packet_index",
        "timestamp",
        "captured_len",
        "wire_len",
        "protocol",
        "src_ip",
        "dst_ip",
        "src_port",
        "dst_port",
        "tcp_flags",
        "flow_eligible",
        "flow_ineligible_reason",
    ]
    assert packet_frame["packet_index"].to_list() == [1, 2, 3]
    assert packet_frame["source_packet_index"].to_list() == [1, 2, 3]
    assert packet_frame["protocol"].to_list() == ["tcp", "arp", "udp"]
    assert packet_frame["flow_eligible"].to_list() == [True, False, True]
    assert packet_frame["flow_ineligible_reason"].to_list() == [None, "missing_ip_layer", None]

    extraction_manifest = pl.read_parquet(extraction_manifest_path)
    assert extraction_manifest.item(0, "total_packets") == 3
    assert extraction_manifest.item(0, "flow_eligible_packets") == 2
    assert extraction_manifest.item(0, "flow_ineligible_packets") == 1


def _write_fixture_pcap(path: Path) -> None:
    base_time = 1_700_000_000.0
    packets = [
        _build_tcp_frame("10.0.0.1", "10.0.0.2", 1111, 80, b"hello"),
        _build_arp_frame(),
        _build_udp_frame("10.0.0.3", "10.0.0.4", 5353, 53, b"world"),
    ]

    with path.open("wb") as handle:
        writer = dpkt.pcap.Writer(handle)
        for offset, packet_bytes in enumerate(packets):
            writer.writepkt(packet_bytes, ts=base_time + offset)
        writer.close()


def _build_tcp_frame(src_ip: str, dst_ip: str, src_port: int, dst_port: int, payload: bytes) -> bytes:
    tcp = dpkt.tcp.TCP(sport=src_port, dport=dst_port, seq=1, flags=dpkt.tcp.TH_SYN, data=payload)
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


def _build_arp_frame() -> bytes:
    arp = dpkt.arp.ARP(
        sha=b"\xaa\xaa\xaa\xaa\xaa\xaa",
        spa=socket.inet_aton("10.0.0.1"),
        tha=b"\x00\x00\x00\x00\x00\x00",
        tpa=socket.inet_aton("10.0.0.2"),
        op=dpkt.arp.ARP_OP_REQUEST,
    )
    ethernet = dpkt.ethernet.Ethernet(
        src=b"\xaa\xaa\xaa\xaa\xaa\xaa",
        dst=b"\xff\xff\xff\xff\xff\xff",
        type=dpkt.ethernet.ETH_TYPE_ARP,
        data=arp,
    )
    return bytes(ethernet)


def _write_config(tmp_path: Path, raw_dir: Path) -> Path:
    config_path = tmp_path / "pipeline.yaml"
    config_path.write_text(
        f"""
dataset:
  dataset_id: fixture_trace
  input_dir: {raw_dir}
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
