"""Tests for the legacy and active CLI surfaces."""

import json
from pathlib import Path
import socket

import dpkt
import polars as pl
import yaml
from network_analysis.cli import main
from network_analysis.pipeline.driver import get_module_catalog


def test_module_catalog_uses_named_modules() -> None:
    module_names = [module.name for module in get_module_catalog()]

    assert module_names == [
        "dataset_registry",
        "ingest",
        "packet_extraction",
        "flow_construction",
        "sampling",
        "metrics",
        "plotting",
    ]


def test_cli_validate_config_reports_defaults(sample_config_path: Path, capsys) -> None:
    exit_code = main(["--config", str(sample_config_path), "validate-config"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Dataset: fixture_trace" in captured.out
    assert "Inactivity timeout: 15s" in captured.out
    assert "Sampling rates: 1:1, 1:10, 1:100" in captured.out


def test_cli_plan_prints_stage_sequence(sample_config_path: Path, capsys) -> None:
    exit_code = main(["--config", str(sample_config_path), "plan"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "dataset_registry" in captured.out
    assert "packet_extraction" in captured.out
    assert "results/tables/fixture_trace_metric_summary.parquet" in captured.out


def test_active_cli_validate_config_reports_resolved_defaults(tmp_path: Path, capsys) -> None:
    datasets_root = tmp_path / "datasets"
    datasets_root.mkdir()

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

sampling:
  rates:
    - 10
  method: systematic
""".strip()
        + "\n",
        encoding="utf-8",
    )

    exit_code = main(
        [
            "--run-config",
            str(run_config_path),
            "--dataset-template",
            str(dataset_template_path),
            "--validate-config",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Dataset template:" in captured.out
    assert "Run config:" in captured.out
    assert "Inactivity timeout: 15s" in captured.out
    assert "Sampling rates: 1:1, 1:10" in captured.out


def test_active_cli_run_executes_end_to_end_pipeline(tmp_path: Path) -> None:
    datasets_root = tmp_path / "datasets"
    dataset_dir = datasets_root / "fixture_trace"
    dataset_dir.mkdir(parents=True)
    capture_path = dataset_dir / "fixture_trace.pcap"
    _write_fixture_pcap(capture_path)

    dataset_template_path = tmp_path / "dataset_template.yaml"
    dataset_template_path.write_text(
        """
discovery:
  dataset_glob: "*"
  raw_glob: "*.pcap"
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

sampling:
  rates:
    - 2
    - 3
  method: systematic

runtime:
  plotting_mode: off
""".strip()
        + "\n",
        encoding="utf-8",
    )

    exit_code = main(
        [
            "--run-config",
            str(run_config_path),
            "--dataset-template",
            str(dataset_template_path),
        ]
    )
    assert exit_code == 0

    metric_summary = tmp_path / "results" / "fixture_trace" / "tables" / "fixture_trace_metric_summary.parquet"
    flow_metrics = tmp_path / "results" / "fixture_trace" / "tables" / "fixture_trace_flow_metrics.parquet"
    meta_dir = tmp_path / "results" / "fixture_trace" / "meta"
    logs_dir = tmp_path / "results" / "fixture_trace" / "logs"
    assert metric_summary.exists()
    assert flow_metrics.exists()
    assert (meta_dir / "resolved_dataset.yaml").exists()
    assert (meta_dir / "run_config.yaml").exists()
    assert (meta_dir / "run_manifest.json").exists()
    assert (meta_dir / "stage_timings.json").exists()
    assert (logs_dir / "run.log").exists()

    summary_frame = pl.read_parquet(metric_summary).sort(["sampling_rate", "size_basis"])
    assert summary_frame["sampling_rate"].to_list() == [1, 2, 3]
    assert summary_frame["flow_detection_rate"].to_list() == [1.0, 0.5, 1.0]

    resolved_dataset = yaml.safe_load((meta_dir / "resolved_dataset.yaml").read_text(encoding="utf-8"))
    run_config_snapshot = yaml.safe_load((meta_dir / "run_config.yaml").read_text(encoding="utf-8"))
    run_manifest = json.loads((meta_dir / "run_manifest.json").read_text(encoding="utf-8"))
    stage_timings = json.loads((meta_dir / "stage_timings.json").read_text(encoding="utf-8"))
    run_log = (logs_dir / "run.log").read_text(encoding="utf-8")

    assert resolved_dataset["dataset_id"] == "fixture_trace"
    assert len(resolved_dataset["capture_files"]) == 1
    assert run_config_snapshot["methodology"]["inactivity_timeout_seconds"] == 15
    assert run_config_snapshot["methodology"]["flow_key_fields"] == [
        "src_ip",
        "dst_ip",
        "src_port",
        "dst_port",
        "protocol",
    ]
    assert run_manifest["status"] == "completed"
    assert run_manifest["dataset_id"] == "fixture_trace"
    assert run_manifest["outputs"]["meta_dir"] == str(meta_dir)
    assert run_manifest["outputs"]["logs_dir"] == str(logs_dir)
    assert set(stage_timings) == {
        "dataset_registry",
        "ingest",
        "packet_extraction",
        "flow_construction",
        "sampling",
        "metrics",
    }
    assert "[active] [1/1] fixture_trace starting" in run_log
    assert "[dataset fixture_trace] [1/6] dataset_registry starting" in run_log
    assert "[dataset fixture_trace] [6/6] metrics completed" in run_log


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
