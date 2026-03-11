"""Ground-truth flow construction module implementation."""

from datetime import datetime
from pathlib import Path

from .artifacts import build_artifact_paths
from .base import ModuleContract
from .config import DatasetRunConfig
from .constants import PREFERRED_TABULAR_FORMAT
from .types import ArtifactContract, ByteBasis, ModuleName

MODULE_CONTRACT = ModuleContract(
    name=ModuleName.FLOW_CONSTRUCTION,
    description="Reconstruct unsampled directional baseline flows from canonical packets.",
    inputs=(
        "canonical packet table",
        "flow-key definition",
        "inactivity timeout",
        "size basis",
    ),
    outputs=(
        ArtifactContract(
            name="baseline_flows",
            relative_path_template="data/processed/{dataset_id}/baseline_flows.parquet",
            format=PREFERRED_TABULAR_FORMAT,
            description="Ground-truth 1:1 baseline flow records.",
        ),
    ),
    implemented=True,
)


def describe_module() -> ModuleContract:
    """Return the static module contract."""

    return MODULE_CONTRACT


def run_module(config: DatasetRunConfig) -> Path:
    """Reconstruct baseline flows from the canonical packet table."""

    import polars as pl

    artifact_paths = build_artifact_paths(config)
    if not artifact_paths.packets.exists():
        raise FileNotFoundError(
            f"Canonical packet table is missing. Run {ModuleName.PACKET_EXTRACTION} first: {artifact_paths.packets}"
        )

    packet_frame = pl.read_parquet(artifact_paths.packets)
    eligible_packets = _prepare_eligible_packets(packet_frame, config)
    if eligible_packets.is_empty():
        raise ValueError("Flow construction found no flow-eligible packets in the packet table.")

    flow_rows = _reconstruct_baseline_flows(eligible_packets, config)
    flow_frame = (
        pl.DataFrame(flow_rows)
        .sort(["start_ts", *config.methodology.flow_key_fields, "flow_sequence"])
        .with_row_index(name="flow_ordinal", offset=1)
        .with_columns(
            pl.concat_str(
                pl.lit(f"{config.dataset.dataset_id}-flow-"),
                pl.col("flow_ordinal").cast(pl.Utf8).str.zfill(6),
            ).alias("flow_id")
        )
        .select(
            "dataset_id",
            "flow_id",
            *config.methodology.flow_key_fields,
            "flow_sequence",
            "start_timestamp_us",
            "end_timestamp_us",
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
        )
    )

    artifact_paths.processed_dir.mkdir(parents=True, exist_ok=True)
    flow_frame.write_parquet(artifact_paths.baseline_flows)
    return artifact_paths.baseline_flows


def _prepare_eligible_packets(packet_frame, config: DatasetRunConfig):
    import polars as pl

    required_fields = (
        "dataset_id",
        "packet_index",
        "timestamp_us",
        "timestamp",
        "captured_len",
        *config.methodology.flow_key_fields,
    )
    missing_fields = [field for field in required_fields if field not in packet_frame.columns]
    if missing_fields:
        raise ValueError(f"Canonical packet table is missing required fields for flow construction: {missing_fields}")

    eligible_packets = (
        packet_frame.filter(pl.col("flow_eligible"))
        .select(
            "dataset_id",
            "packet_index",
            "timestamp_us",
            "timestamp",
            "captured_len",
            "wire_len",
            *config.methodology.flow_key_fields,
        )
        .sort([*config.methodology.flow_key_fields, "timestamp_us", "packet_index"])
    )
    if eligible_packets.is_empty():
        return eligible_packets

    null_key_fields = [
        field
        for field in config.methodology.flow_key_fields
        if eligible_packets.filter(pl.col(field).is_null()).height > 0
    ]
    if null_key_fields:
        raise ValueError(
            "Flow-eligible packets contain null values for configured flow-key fields: "
            f"{', '.join(null_key_fields)}"
        )

    return eligible_packets


def _reconstruct_baseline_flows(packet_frame, config: DatasetRunConfig) -> list[dict[str, object]]:
    flow_key_fields = config.methodology.flow_key_fields
    timeout_seconds = float(config.methodology.inactivity_timeout_seconds)
    byte_field = _resolve_byte_field(config.methodology.byte_basis)
    flow_rows: list[dict[str, object]] = []

    current_state: dict[str, object] | None = None
    current_key: tuple[object, ...] | None = None
    flow_sequence = 0

    for row in packet_frame.iter_rows(named=True):
        key = tuple(row[field] for field in flow_key_fields)
        timestamp_us = int(row["timestamp_us"])
        timestamp = _normalize_timestamp(row["timestamp"])
        packet_index = int(row["packet_index"])
        packet_bytes = int(row[byte_field])

        if current_state is None or current_key != key:
            if current_state is not None:
                flow_rows.append(_finalize_flow_row(current_state, config))
            current_key = key
            flow_sequence = 1
            current_state = _start_flow_state(
                row,
                timestamp_us,
                timestamp,
                packet_index,
                packet_bytes,
                flow_sequence,
            )
            continue

        gap_seconds = (timestamp_us - current_state["end_timestamp_us"]) / 1_000_000
        if gap_seconds > timeout_seconds:
            flow_rows.append(_finalize_flow_row(current_state, config))
            flow_sequence += 1
            current_state = _start_flow_state(
                row,
                timestamp_us,
                timestamp,
                packet_index,
                packet_bytes,
                flow_sequence,
            )
            continue

        current_state["end_ts"] = timestamp
        current_state["end_timestamp_us"] = timestamp_us
        current_state["end_packet_index"] = packet_index
        current_state["packet_count"] += 1
        current_state["byte_count"] += packet_bytes

    if current_state is not None:
        flow_rows.append(_finalize_flow_row(current_state, config))

    return flow_rows


def _start_flow_state(
    row: dict[str, object],
    timestamp_us: int,
    timestamp: datetime,
    packet_index: int,
    packet_bytes: int,
    flow_sequence: int,
) -> dict[str, object]:
    return {
        "dataset_id": str(row["dataset_id"]),
        "flow_key": {
            field: row[field]
            for field in row
            if field
            not in {"dataset_id", "packet_index", "timestamp_us", "timestamp", "captured_len", "wire_len"}
        },
        "flow_sequence": flow_sequence,
        "start_timestamp_us": timestamp_us,
        "start_ts": timestamp,
        "end_ts": timestamp,
        "end_timestamp_us": timestamp_us,
        "start_packet_index": packet_index,
        "end_packet_index": packet_index,
        "packet_count": 1,
        "byte_count": packet_bytes,
    }


def _finalize_flow_row(state: dict[str, object], config: DatasetRunConfig) -> dict[str, object]:
    start_ts = state["start_ts"]
    end_ts = state["end_ts"]
    duration_seconds = (end_ts - start_ts).total_seconds()
    packet_count = int(state["packet_count"])
    byte_count = int(state["byte_count"])

    row = {
        "dataset_id": state["dataset_id"],
        **state["flow_key"],
        "flow_sequence": int(state["flow_sequence"]),
        "start_timestamp_us": int(state["start_timestamp_us"]),
        "end_timestamp_us": int(state["end_timestamp_us"]),
        "start_ts": start_ts,
        "end_ts": end_ts,
        "start_packet_index": int(state["start_packet_index"]),
        "end_packet_index": int(state["end_packet_index"]),
        "duration_seconds": float(duration_seconds),
        "packet_count": packet_count,
        "byte_count": byte_count,
        "sending_rate_packets_per_second": None,
        "sending_rate_bytes_per_second": None,
        "size_basis": str(config.methodology.size_basis),
        "byte_basis": str(config.methodology.byte_basis),
    }

    if duration_seconds > 0:
        row["sending_rate_packets_per_second"] = packet_count / duration_seconds
        row["sending_rate_bytes_per_second"] = byte_count / duration_seconds

    return row


def _resolve_byte_field(byte_basis: ByteBasis) -> str:
    if byte_basis == ByteBasis.CAPTURED_LEN:
        return "captured_len"
    raise ValueError(f"Unsupported byte basis for flow construction: {byte_basis}")


def _normalize_timestamp(value: object) -> datetime:
    if not isinstance(value, datetime):
        raise TypeError(f"Expected packet timestamps to be datetimes, got {type(value)!r}")
    return value
