"""Metric computation module implementation."""

from dataclasses import dataclass
from pathlib import Path

from .base import ModuleContract
from ..shared.artifacts import build_artifact_paths
from ..shared.constants import PREFERRED_TABULAR_FORMAT
from ..shared.config import PipelineConfig
from ..shared.types import ArtifactContract, ByteBasis, ModuleName, SizeBasis

MODULE_CONTRACT = ModuleContract(
    name=ModuleName.METRICS,
    description="Compare each 1:X sampled run directly against the 1:1 baseline.",
    inputs=(
        "baseline flows",
        "sampling run manifest",
        "sampled packet tables",
        "size basis",
        "flow-key definition",
        "inactivity timeout",
    ),
    outputs=(
        ArtifactContract(
            name="metric_summary",
            relative_path_template="results/tables/{dataset_id}_metric_summary.parquet",
            format=PREFERRED_TABULAR_FORMAT,
            description="Per-rate summary metrics including detection rate.",
        ),
        ArtifactContract(
            name="flow_metrics",
            relative_path_template="results/tables/{dataset_id}_flow_metrics.parquet",
            format=PREFERRED_TABULAR_FORMAT,
            description="Per-flow distortion metrics matched against the baseline.",
        ),
    ),
    implemented=True,
)


def describe_module() -> ModuleContract:
    """Return the static module contract."""

    return MODULE_CONTRACT


@dataclass(frozen=True)
class BaselineFlowRecord:
    """Baseline flow fields required for sampled-packet matching and metric computation."""

    flow_id: str
    flow_key: tuple[object, ...]
    start_timestamp_us: int
    end_timestamp_us: int
    duration_seconds: float
    packet_count: int
    byte_count: int
    sending_rate_packets_per_second: float | None
    sending_rate_bytes_per_second: float | None


def run_module(config: PipelineConfig) -> tuple[Path, Path]:
    """Compare sampled packet observations against the fixed baseline flow table."""

    import polars as pl

    artifact_paths = build_artifact_paths(config)
    if not artifact_paths.baseline_flows.exists():
        raise FileNotFoundError(
            f"Baseline flow table is missing. Run {ModuleName.FLOW_CONSTRUCTION} first: {artifact_paths.baseline_flows}"
        )
    if not artifact_paths.sampling_manifest.exists():
        raise FileNotFoundError(
            f"Sampling manifest is missing. Run {ModuleName.SAMPLING} first: {artifact_paths.sampling_manifest}"
        )

    baseline_frame = pl.read_parquet(artifact_paths.baseline_flows)
    sampling_manifest = pl.read_parquet(artifact_paths.sampling_manifest).sort("sampling_rate")
    if baseline_frame.is_empty():
        raise ValueError("Metrics found no baseline flows.")
    if sampling_manifest.is_empty():
        raise ValueError("Metrics found no sampling runs.")

    baseline_records, baseline_by_key = _prepare_baseline_records(baseline_frame, config)
    summary_rows: list[dict[str, object]] = []
    flow_metric_rows: list[dict[str, object]] = []

    for sampling_run in sampling_manifest.iter_rows(named=True):
        sampling_rate = int(sampling_run["sampling_rate"])
        sampling_method = str(sampling_run["sampling_method"])
        random_seed = sampling_run["random_seed"]
        sampled_packets_path = Path(str(sampling_run["sampled_packets_path"]))
        sampled_packet_frame = pl.read_parquet(sampled_packets_path)

        matched_packets = _match_sampled_packets_to_baseline(sampled_packet_frame, baseline_by_key, config)
        detected_flow_count = sum(1 for packets in matched_packets.values() if packets)
        baseline_flow_count = len(baseline_records)
        undetected_flow_count = baseline_flow_count - detected_flow_count

        for size_basis in config.methodology.requested_size_bases():
            summary_rows.append(
                {
                    "dataset_id": config.dataset.dataset_id,
                    "sampling_rate": sampling_rate,
                    "sampling_method": sampling_method,
                    "random_seed": random_seed,
                    "baseline_flow_count": baseline_flow_count,
                    "detected_flow_count": detected_flow_count,
                    "undetected_flow_count": undetected_flow_count,
                    "flow_detection_rate": detected_flow_count / baseline_flow_count,
                    "sampled_packet_count": int(sampling_run["sampled_packet_count"]),
                    "sampled_flow_count": int(sampling_run["sampled_flow_count"]),
                    "size_basis": size_basis.value,
                    "byte_basis": config.methodology.byte_basis.value,
                }
            )

            for record in baseline_records:
                flow_metric_rows.append(
                    _build_flow_metric_row(
                        config=config,
                        baseline_record=record,
                        sampled_packets=matched_packets[record.flow_id],
                        sampling_rate=sampling_rate,
                        sampling_method=sampling_method,
                        random_seed=random_seed,
                        size_basis=size_basis,
                    )
                )

    artifact_paths.results_tables_dir.mkdir(parents=True, exist_ok=True)
    summary_frame = pl.DataFrame(summary_rows).sort(["sampling_rate", "size_basis"])
    flow_metrics_frame = pl.DataFrame(flow_metric_rows).sort(["sampling_rate", "size_basis", "flow_id"])
    summary_frame.write_parquet(artifact_paths.metric_summary)
    flow_metrics_frame.write_parquet(artifact_paths.flow_metrics)
    return artifact_paths.metric_summary, artifact_paths.flow_metrics


def _prepare_baseline_records(baseline_frame, config: PipelineConfig) -> tuple[list[BaselineFlowRecord], dict[tuple[object, ...], list[BaselineFlowRecord]]]:
    required_fields = (
        "flow_id",
        "start_timestamp_us",
        "end_timestamp_us",
        "duration_seconds",
        "packet_count",
        "byte_count",
        "sending_rate_packets_per_second",
        "sending_rate_bytes_per_second",
        *config.methodology.flow_key_fields,
    )
    missing_fields = [field for field in required_fields if field not in baseline_frame.columns]
    if missing_fields:
        raise ValueError(f"Baseline flow table is missing required metric fields: {missing_fields}")

    records: list[BaselineFlowRecord] = []
    by_key: dict[tuple[object, ...], list[BaselineFlowRecord]] = {}
    for row in baseline_frame.sort([*config.methodology.flow_key_fields, "start_timestamp_us"]).iter_rows(named=True):
        record = BaselineFlowRecord(
            flow_id=str(row["flow_id"]),
            flow_key=tuple(row[field] for field in config.methodology.flow_key_fields),
            start_timestamp_us=int(row["start_timestamp_us"]),
            end_timestamp_us=int(row["end_timestamp_us"]),
            duration_seconds=float(row["duration_seconds"]),
            packet_count=int(row["packet_count"]),
            byte_count=int(row["byte_count"]),
            sending_rate_packets_per_second=(
                None
                if row["sending_rate_packets_per_second"] is None
                else float(row["sending_rate_packets_per_second"])
            ),
            sending_rate_bytes_per_second=(
                None
                if row["sending_rate_bytes_per_second"] is None
                else float(row["sending_rate_bytes_per_second"])
            ),
        )
        records.append(record)
        by_key.setdefault(record.flow_key, []).append(record)

    return records, by_key


def _match_sampled_packets_to_baseline(sampled_packet_frame, baseline_by_key, config: PipelineConfig) -> dict[str, list[dict[str, int]]]:
    import polars as pl

    matched_packets = {
        record.flow_id: []
        for records in baseline_by_key.values()
        for record in records
    }
    if sampled_packet_frame.is_empty():
        return matched_packets

    eligible_packets = sampled_packet_frame.filter(pl.col("flow_eligible"))
    for row in eligible_packets.iter_rows(named=True):
        key = tuple(row[field] for field in config.methodology.flow_key_fields)
        timestamp_us = int(row["timestamp_us"])
        candidates = baseline_by_key.get(key, [])
        matched_flow = next(
            (
                candidate
                for candidate in candidates
                if candidate.start_timestamp_us <= timestamp_us <= candidate.end_timestamp_us
            ),
            None,
        )
        if matched_flow is None:
            raise ValueError(
                "A sampled packet could not be matched to any baseline flow interval for the configured flow key."
            )

        matched_packets[matched_flow.flow_id].append(
            {
                "timestamp_us": timestamp_us,
                "captured_len": int(row["captured_len"]),
            }
        )

    return matched_packets


def _build_flow_metric_row(
    *,
    config: PipelineConfig,
    baseline_record: BaselineFlowRecord,
    sampled_packets: list[dict[str, int]],
    sampling_rate: int,
    sampling_method: str,
    random_seed: object,
    size_basis: SizeBasis,
) -> dict[str, object]:
    baseline_size = _baseline_size_for_basis(baseline_record, size_basis)
    baseline_sending_rate = _baseline_sending_rate_for_basis(baseline_record, size_basis)

    if not sampled_packets:
        return {
            "dataset_id": config.dataset.dataset_id,
            "sampling_rate": sampling_rate,
            "sampling_method": sampling_method,
            "random_seed": random_seed,
            "flow_id": baseline_record.flow_id,
            "detection_status": "undetected",
            "size_basis": size_basis.value,
            "byte_basis": config.methodology.byte_basis.value,
            "baseline_size": float(baseline_size),
            "sampled_size_estimate": None,
            "baseline_duration_seconds": baseline_record.duration_seconds,
            "sampled_duration_seconds": None,
            "baseline_sending_rate": baseline_sending_rate,
            "sampled_sending_rate": None,
            "flow_size_overestimation_factor": None,
            "flow_duration_underestimation_factor": None,
            "flow_sending_rate_overestimation_factor": None,
        }

    sampled_packets.sort(key=lambda row: row["timestamp_us"])
    sampled_duration_seconds = (
        sampled_packets[-1]["timestamp_us"] - sampled_packets[0]["timestamp_us"]
    ) / 1_000_000
    observed_packet_count = len(sampled_packets)
    observed_byte_count = sum(packet["captured_len"] for packet in sampled_packets)
    sampled_size_estimate = _estimated_size_for_basis(
        observed_packet_count=observed_packet_count,
        observed_byte_count=observed_byte_count,
        sampling_rate=sampling_rate,
        size_basis=size_basis,
    )
    sampled_sending_rate = None
    if sampled_duration_seconds > 0:
        sampled_sending_rate = sampled_size_estimate / sampled_duration_seconds

    size_factor = sampled_size_estimate / baseline_size
    duration_factor = None
    if baseline_record.duration_seconds > 0:
        duration_factor = sampled_duration_seconds / baseline_record.duration_seconds

    sending_rate_factor = None
    if size_factor is not None and duration_factor not in {None, 0}:
        sending_rate_factor = size_factor / duration_factor

    return {
        "dataset_id": config.dataset.dataset_id,
        "sampling_rate": sampling_rate,
        "sampling_method": sampling_method,
        "random_seed": random_seed,
        "flow_id": baseline_record.flow_id,
        "detection_status": "detected",
        "size_basis": size_basis.value,
        "byte_basis": config.methodology.byte_basis.value,
        "baseline_size": float(baseline_size),
        "sampled_size_estimate": float(sampled_size_estimate),
        "baseline_duration_seconds": baseline_record.duration_seconds,
        "sampled_duration_seconds": float(sampled_duration_seconds),
        "baseline_sending_rate": baseline_sending_rate,
        "sampled_sending_rate": sampled_sending_rate,
        "flow_size_overestimation_factor": float(size_factor),
        "flow_duration_underestimation_factor": duration_factor,
        "flow_sending_rate_overestimation_factor": sending_rate_factor,
    }


def _baseline_size_for_basis(record: BaselineFlowRecord, size_basis: SizeBasis) -> int:
    if size_basis == SizeBasis.PACKETS:
        return record.packet_count
    if size_basis == SizeBasis.BYTES:
        return record.byte_count
    raise ValueError(f"Unsupported size basis for metrics: {size_basis}")


def _baseline_sending_rate_for_basis(record: BaselineFlowRecord, size_basis: SizeBasis) -> float | None:
    if size_basis == SizeBasis.PACKETS:
        return record.sending_rate_packets_per_second
    if size_basis == SizeBasis.BYTES:
        return record.sending_rate_bytes_per_second
    raise ValueError(f"Unsupported size basis for metrics: {size_basis}")


def _estimated_size_for_basis(
    *,
    observed_packet_count: int,
    observed_byte_count: int,
    sampling_rate: int,
    size_basis: SizeBasis,
) -> int:
    if size_basis == SizeBasis.PACKETS:
        return observed_packet_count * sampling_rate
    if size_basis == SizeBasis.BYTES:
        return observed_byte_count * sampling_rate
    raise ValueError(f"Unsupported size basis for metrics: {size_basis}")
