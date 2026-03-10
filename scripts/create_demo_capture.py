"""Create a deterministic tiny full-trace PCAP for local MVP validation."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import socket
from typing import Sequence

try:
    import dpkt
except ImportError as exc:  # pragma: no cover - depends on local environment
    raise SystemExit(
        "dpkt is required to generate the demo capture. Install project dependencies first."
    ) from exc


DEFAULT_OUTPUT = Path("data/raw/demo_trace/demo_trace.pcap")
BASE_TIMESTAMP = 1_700_000_000.0


@dataclass(frozen=True)
class PacketSpec:
    """One synthetic packet in the demo trace."""

    timestamp_offset: float
    src_ip: str
    dst_ip: str
    protocol: str
    src_port: int
    dst_port: int
    payload: bytes


PACKET_SPECS: tuple[PacketSpec, ...] = (
    PacketSpec(0.0, "10.0.0.1", "10.0.0.2", "tcp", 12345, 80, b"flow-a-1"),
    PacketSpec(1.0, "10.0.0.3", "10.0.0.4", "udp", 5000, 53, b"flow-b-1"),
    PacketSpec(5.0, "10.0.0.1", "10.0.0.2", "tcp", 12345, 80, b"flow-a-2"),
    PacketSpec(8.0, "10.0.0.5", "10.0.0.6", "tcp", 44321, 443, b"flow-c-1"),
    PacketSpec(12.0, "10.0.0.3", "10.0.0.4", "udp", 5000, 53, b"flow-b-2"),
    PacketSpec(22.0, "10.0.0.1", "10.0.0.2", "tcp", 12345, 80, b"flow-a-3"),
    PacketSpec(23.0, "10.0.0.7", "10.0.0.8", "udp", 6000, 161, b"flow-d-1"),
    PacketSpec(30.0, "10.0.0.1", "10.0.0.2", "tcp", 12345, 80, b"flow-a-4"),
)


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI parser."""

    parser = argparse.ArgumentParser(
        description="Generate a deterministic tiny full-trace PCAP for the MVP demo pipeline.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="PCAP output path. Defaults to data/raw/demo_trace/demo_trace.pcap.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow overwriting an existing demo capture.",
    )
    return parser


def build_packets() -> list[tuple[float, bytes]]:
    """Create the synthetic packets with fixed timestamps and 5-tuples."""

    return [
        (BASE_TIMESTAMP + spec.timestamp_offset, _build_frame_bytes(spec))
        for spec in PACKET_SPECS
    ]


def write_demo_capture(output_path: Path, *, overwrite: bool = False) -> Path:
    """Write the synthetic trace to disk."""

    output_path = output_path.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_path.exists() and not overwrite:
        raise FileExistsError(
            f"{output_path} already exists. Use --overwrite if you intentionally want to replace it."
        )

    with output_path.open("wb") as handle:
        writer = dpkt.pcap.Writer(handle)
        for timestamp, packet_bytes in build_packets():
            writer.writepkt(packet_bytes, ts=timestamp)
        writer.close()
    return output_path


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entrypoint."""

    args = build_parser().parse_args(argv)
    output_path = write_demo_capture(args.output, overwrite=args.overwrite)
    print(f"Wrote deterministic demo capture to {output_path}")
    print(f"Packet count: {len(PACKET_SPECS)}")
    print("Configured baseline-relevant behaviours:")
    print("- directional 5-tuple flow key")
    print("- 15-second inactivity timeout")
    print("- repeated TCP 5-tuple separated by a >15s gap to force one flow split")
    print("- additional UDP and single-packet flows for detection edge cases")
    return 0


def _build_frame_bytes(spec: PacketSpec) -> bytes:
    if spec.protocol == "tcp":
        transport = dpkt.tcp.TCP(
            sport=spec.src_port,
            dport=spec.dst_port,
            seq=1,
            flags=dpkt.tcp.TH_ACK,
            data=spec.payload,
        )
        transport.off = 5
        ip_proto = dpkt.ip.IP_PROTO_TCP
    else:
        transport = dpkt.udp.UDP(
            sport=spec.src_port,
            dport=spec.dst_port,
            data=spec.payload,
        )
        transport.ulen = len(transport)
        ip_proto = dpkt.ip.IP_PROTO_UDP

    ip = dpkt.ip.IP(
        src=socket.inet_aton(spec.src_ip),
        dst=socket.inet_aton(spec.dst_ip),
        p=ip_proto,
        ttl=64,
        data=transport,
    )
    ip.len = len(ip)

    ethernet = dpkt.ethernet.Ethernet(
        src=b"\xaa\xaa\xaa\xaa\xaa\xaa",
        dst=b"\xbb\xbb\xbb\xbb\xbb\xbb",
        type=dpkt.ethernet.ETH_TYPE_IP,
        data=ip,
    )
    return bytes(ethernet)


if __name__ == "__main__":
    raise SystemExit(main())
