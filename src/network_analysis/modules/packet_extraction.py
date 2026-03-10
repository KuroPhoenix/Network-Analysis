"""Packet extraction module implementation."""

from datetime import UTC, datetime
from pathlib import Path
import socket

from .base import ModuleContract
from ..shared.artifacts import build_artifact_paths
from ..shared.constants import PREFERRED_TABULAR_FORMAT
from ..shared.config import PipelineConfig
from ..shared.types import ArtifactContract, CaptureFormat, ModuleName

MODULE_CONTRACT = ModuleContract(
    name=ModuleName.PACKET_EXTRACTION,
    description="Extract canonical packet metadata tables from staged packet captures.",
    inputs=(
        "ingest manifest",
        "staged capture files",
        "packet parser configuration",
    ),
    outputs=(
        ArtifactContract(
            name="canonical_packet_table",
            relative_path_template="data/processed/{dataset_id}/packets.parquet",
            format=PREFERRED_TABULAR_FORMAT,
            description="Canonical packet table used by downstream flow reconstruction.",
        ),
        ArtifactContract(
            name="packet_extraction_manifest",
            relative_path_template="data/processed/{dataset_id}/packet_extraction_manifest.parquet",
            format=PREFERRED_TABULAR_FORMAT,
            description="Extraction metadata including eligible and ineligible packet counts.",
        ),
    ),
    implemented=True,
)


def describe_module() -> ModuleContract:
    """Return the static module contract."""

    return MODULE_CONTRACT


def run_module(config: PipelineConfig) -> tuple[Path, Path]:
    """Extract a canonical packet table from staged capture files."""

    import polars as pl

    artifact_paths = build_artifact_paths(config)
    if not artifact_paths.ingest_manifest.exists():
        raise FileNotFoundError(
            f"Ingest manifest is missing. Run {ModuleName.INGEST} first: {artifact_paths.ingest_manifest}"
        )

    ingest_manifest = pl.read_parquet(artifact_paths.ingest_manifest).sort(
        ["source_discovery_index", "source_member_index"]
    )
    if ingest_manifest.is_empty():
        raise ValueError("Ingest manifest is empty.")

    packet_rows: list[dict[str, object]] = []
    for row in ingest_manifest.iter_rows(named=True):
        packet_rows.extend(
            _extract_packets_from_file(
                dataset_id=config.dataset.dataset_id,
                staged_file=Path(str(row["staged_file"])),
                capture_format=CaptureFormat(str(row["capture_format"])),
                source_discovery_index=int(row["source_discovery_index"]),
                source_member_index=int(row["source_member_index"]),
            )
        )

    if not packet_rows:
        raise ValueError("Packet extraction found no packets in the staged capture files.")

    packet_frame = (
        pl.DataFrame(packet_rows)
        .sort(["source_discovery_index", "source_member_index", "source_packet_index"])
        .with_row_index(name="packet_index", offset=1)
        .with_columns(
            pl.col("packet_index").cast(pl.Int64),
            pl.col("source_discovery_index").cast(pl.Int64),
            pl.col("source_member_index").cast(pl.Int64),
            pl.col("source_packet_index").cast(pl.Int64),
            pl.col("timestamp_us").cast(pl.Int64),
            pl.col("captured_len").cast(pl.Int64),
            pl.col("wire_len").cast(pl.Int64),
        )
        .select(
            "dataset_id",
            "source_discovery_index",
            "source_member_index",
            "source_file",
            "packet_index",
            "source_packet_index",
            "timestamp_us",
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
        )
    )
    artifact_paths.processed_dir.mkdir(parents=True, exist_ok=True)
    packet_frame.write_parquet(artifact_paths.packets)

    metadata_frame = pl.DataFrame(
        [
            {
                "dataset_id": config.dataset.dataset_id,
                "source_file_count": ingest_manifest.height,
                "total_packets": packet_frame.height,
                "flow_eligible_packets": packet_frame.filter(pl.col("flow_eligible")).height,
                "flow_ineligible_packets": packet_frame.filter(~pl.col("flow_eligible")).height,
                "earliest_timestamp": packet_frame["timestamp"].min(),
                "latest_timestamp": packet_frame["timestamp"].max(),
            }
        ]
    )
    metadata_frame.write_parquet(artifact_paths.packet_extraction_manifest)

    return artifact_paths.packets, artifact_paths.packet_extraction_manifest


def _extract_packets_from_file(
    *,
    dataset_id: str,
    staged_file: Path,
    capture_format: CaptureFormat,
    source_discovery_index: int,
    source_member_index: int,
) -> list[dict[str, object]]:
    reader_factory = _build_reader_factory(staged_file, capture_format)
    rows: list[dict[str, object]] = []

    with staged_file.open("rb") as handle:
        packets = reader_factory(handle)
        for source_packet_index, (timestamp_seconds, packet_bytes) in enumerate(packets, start=1):
            rows.append(
                _extract_packet_row(
                    dataset_id=dataset_id,
                    staged_file=staged_file,
                    source_discovery_index=source_discovery_index,
                    source_member_index=source_member_index,
                    source_packet_index=source_packet_index,
                    timestamp_seconds=float(timestamp_seconds),
                    packet_bytes=packet_bytes,
                )
            )

    return rows


def _build_reader_factory(staged_file: Path, capture_format: CaptureFormat):
    import dpkt

    if capture_format == CaptureFormat.PCAP:
        return dpkt.pcap.Reader
    if capture_format == CaptureFormat.PCAPNG:
        return dpkt.pcapng.Reader
    raise ValueError(f"Unsupported capture format for packet extraction: {staged_file}")


def _extract_packet_row(
    *,
    dataset_id: str,
    staged_file: Path,
    source_discovery_index: int,
    source_member_index: int,
    source_packet_index: int,
    timestamp_seconds: float,
    packet_bytes: bytes,
) -> dict[str, object]:
    import dpkt

    timestamp_us = int(round(timestamp_seconds * 1_000_000))
    timestamp = datetime.fromtimestamp(timestamp_us / 1_000_000, UTC)
    captured_len = len(packet_bytes)
    wire_len = None

    src_ip: str | None = None
    dst_ip: str | None = None
    src_port: int | None = None
    dst_port: int | None = None
    tcp_flags: str | None = None
    flow_eligible = False
    flow_ineligible_reason: str | None = None

    ethernet_frame = dpkt.ethernet.Ethernet(packet_bytes)
    if isinstance(ethernet_frame.data, dpkt.ip.IP):
        ip_layer = ethernet_frame.data
        src_ip = socket.inet_ntoa(ip_layer.src)
        dst_ip = socket.inet_ntoa(ip_layer.dst)
    elif isinstance(ethernet_frame.data, dpkt.ip6.IP6):
        ip_layer = ethernet_frame.data
        src_ip = socket.inet_ntop(socket.AF_INET6, ip_layer.src)
        dst_ip = socket.inet_ntop(socket.AF_INET6, ip_layer.dst)
    else:
        ip_layer = None

    if ip_layer is not None and isinstance(ip_layer.data, dpkt.tcp.TCP):
        transport = ip_layer.data
        protocol = "tcp"
        src_port = int(transport.sport)
        dst_port = int(transport.dport)
        tcp_flags = str(transport.flags)
        flow_eligible = True
    elif ip_layer is not None and isinstance(ip_layer.data, dpkt.udp.UDP):
        transport = ip_layer.data
        protocol = "udp"
        src_port = int(transport.sport)
        dst_port = int(transport.dport)
        flow_eligible = True
    else:
        protocol = _infer_protocol_name(ethernet_frame, ip_layer)
        if ip_layer is None:
            flow_ineligible_reason = "missing_ip_layer"
        else:
            flow_ineligible_reason = "unsupported_transport_for_default_5tuple"

    return {
        "dataset_id": dataset_id,
        "source_discovery_index": source_discovery_index,
        "source_member_index": source_member_index,
        "source_file": str(staged_file),
        "source_packet_index": source_packet_index,
        "timestamp_us": timestamp_us,
        "timestamp": timestamp,
        "captured_len": captured_len,
        "wire_len": wire_len,
        "protocol": protocol,
        "src_ip": src_ip,
        "dst_ip": dst_ip,
        "src_port": src_port,
        "dst_port": dst_port,
        "tcp_flags": tcp_flags,
        "flow_eligible": flow_eligible,
        "flow_ineligible_reason": flow_ineligible_reason,
    }


def _infer_protocol_name(ethernet_frame, ip_layer) -> str:
    import dpkt

    if ip_layer is None:
        if isinstance(ethernet_frame.data, dpkt.arp.ARP):
            return "arp"
        return "non_ip"

    if hasattr(ip_layer, "proto"):
        return f"ip_proto_{int(ip_layer.proto)}"
    if hasattr(ip_layer, "nh"):
        return f"ipv6_next_header_{int(ip_layer.nh)}"

    return ethernet_frame.data.__class__.__name__.lower()
