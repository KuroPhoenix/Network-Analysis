"""Sampling module implementation."""

from pathlib import Path
import random

from .base import ModuleContract
from .flow_construction import _prepare_eligible_packets, _reconstruct_baseline_flows
from ..shared.artifacts import build_artifact_paths
from ..shared.constants import PREFERRED_TABULAR_FORMAT
from ..shared.config import PipelineConfig
from ..shared.types import ArtifactContract, ArtifactKind, ModuleName, SamplingMethod

MODULE_CONTRACT = ModuleContract(
    name=ModuleName.SAMPLING,
    description="Generate sampled packet or flow artefacts for configured 1:X rates.",
    inputs=(
        "canonical packet table",
        "baseline flows",
        "sampling rates",
        "sampling method",
        "random seed when applicable",
    ),
    outputs=(
        ArtifactContract(
            name="sampled_packets",
            relative_path_template="data/processed/{dataset_id}/sampled_packets/",
            format=PREFERRED_TABULAR_FORMAT,
            description="Directory for per-rate sampled packet tables.",
            kind=ArtifactKind.DIRECTORY,
        ),
        ArtifactContract(
            name="sampled_flows",
            relative_path_template="data/processed/{dataset_id}/sampled_flows/",
            format=PREFERRED_TABULAR_FORMAT,
            description="Directory for per-rate sampled flow tables.",
            kind=ArtifactKind.DIRECTORY,
        ),
        ArtifactContract(
            name="sampling_run_manifest",
            relative_path_template="data/processed/{dataset_id}/sampling_runs.parquet",
            format=PREFERRED_TABULAR_FORMAT,
            description="Structured metadata for each sampling run.",
        ),
    ),
    implemented=True,
)


def describe_module() -> ModuleContract:
    """Return the static module contract."""

    return MODULE_CONTRACT


def run_module(config: PipelineConfig) -> tuple[Path, Path, Path]:
    """Generate sampled packet and sampled flow artefacts for each configured rate."""

    import polars as pl

    artifact_paths = build_artifact_paths(config)
    if not artifact_paths.packets.exists():
        raise FileNotFoundError(
            f"Canonical packet table is missing. Run {ModuleName.PACKET_EXTRACTION} first: {artifact_paths.packets}"
        )
    if not artifact_paths.baseline_flows.exists():
        raise FileNotFoundError(
            f"Baseline flow table is missing. Run {ModuleName.FLOW_CONSTRUCTION} first: {artifact_paths.baseline_flows}"
        )

    packet_frame = pl.read_parquet(artifact_paths.packets)
    baseline_flow_frame = pl.read_parquet(artifact_paths.baseline_flows)
    if packet_frame.is_empty():
        raise ValueError("Sampling found no packets in the canonical packet table.")
    if baseline_flow_frame.is_empty():
        raise ValueError("Sampling found no baseline flows to compare against.")

    artifact_paths.sampled_packets_dir.mkdir(parents=True, exist_ok=True)
    artifact_paths.sampled_flows_dir.mkdir(parents=True, exist_ok=True)
    artifact_paths.processed_dir.mkdir(parents=True, exist_ok=True)

    manifest_rows: list[dict[str, object]] = []
    for rate in config.sampling.normalized_rates():
        sampled_packet_frame = _sample_packets(packet_frame, config, rate)
        sampled_packets_path = _resolve_sampled_packets_path(config, artifact_paths.sampled_packets_dir, rate)
        sampled_packet_frame.write_parquet(sampled_packets_path)

        sampled_flow_frame = _reconstruct_sampled_flows(sampled_packet_frame, config, rate)
        sampled_flows_path = _resolve_sampled_flows_path(config, artifact_paths.sampled_flows_dir, rate)
        sampled_flow_frame.write_parquet(sampled_flows_path)

        manifest_rows.append(
            {
                "dataset_id": config.dataset.dataset_id,
                "sampling_rate": rate,
                "sampling_method": config.sampling.method.value,
                "random_seed": config.sampling.random_seed,
                "sampled_packets_path": str(sampled_packets_path),
                "sampled_flows_path": str(sampled_flows_path),
                "sampled_packet_count": sampled_packet_frame.height,
                "flow_eligible_sampled_packet_count": sampled_packet_frame.filter(pl.col("flow_eligible")).height,
                "sampled_flow_count": sampled_flow_frame.height,
                "size_basis": config.methodology.size_basis.value,
                "byte_basis": config.methodology.byte_basis.value,
            }
        )

    pl.DataFrame(manifest_rows).sort("sampling_rate").write_parquet(artifact_paths.sampling_manifest)
    return artifact_paths.sampled_packets_dir, artifact_paths.sampled_flows_dir, artifact_paths.sampling_manifest


def _sample_packets(packet_frame, config: PipelineConfig, rate: int):
    import polars as pl

    if rate < 1:
        raise ValueError(f"Sampling rates must be positive integers, got {rate}")

    if rate == 1:
        sampled_frame = packet_frame.clone()
    elif config.sampling.method == SamplingMethod.SYSTEMATIC:
        sampled_frame = packet_frame.filter(((pl.col("packet_index") - 1) % rate) == 0)
    elif config.sampling.method == SamplingMethod.RANDOM:
        if config.sampling.random_seed is None:
            raise ValueError("Random sampling requires sampling.random_seed to remain reproducible.")
        rng = random.Random(config.sampling.random_seed + rate)
        mask = [rng.randrange(rate) == 0 for _ in range(packet_frame.height)]
        sampled_frame = packet_frame.filter(pl.Series("selected_by_random_sampler", mask))
    else:
        raise ValueError(f"Unsupported sampling method: {config.sampling.method}")

    return sampled_frame.with_columns(
        pl.lit(rate).cast(pl.Int64).alias("sampling_rate"),
        pl.lit(config.sampling.method.value).alias("sampling_method"),
        pl.lit(config.sampling.random_seed).cast(pl.Int64).alias("random_seed"),
    ).select(
        "dataset_id",
        "sampling_rate",
        "sampling_method",
        "random_seed",
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


def _reconstruct_sampled_flows(sampled_packet_frame, config: PipelineConfig, rate: int):
    import polars as pl

    if sampled_packet_frame.is_empty():
        return _empty_sampled_flow_frame()

    eligible_packets = _prepare_eligible_packets(sampled_packet_frame, config)
    if eligible_packets.is_empty():
        return _empty_sampled_flow_frame()

    flow_rows = _reconstruct_baseline_flows(eligible_packets, config)
    if not flow_rows:
        return _empty_sampled_flow_frame()

    return (
        pl.DataFrame(flow_rows)
        .sort(["start_ts", *config.methodology.flow_key_fields, "flow_sequence"])
        .with_row_index(name="sampled_flow_ordinal", offset=1)
        .with_columns(
            pl.lit(rate).cast(pl.Int64).alias("sampling_rate"),
            pl.lit(config.sampling.method.value).alias("sampling_method"),
            pl.lit(config.sampling.random_seed).cast(pl.Int64).alias("random_seed"),
            pl.concat_str(
                pl.lit(f"{config.dataset.dataset_id}-{rate}x-sampled-flow-"),
                pl.col("sampled_flow_ordinal").cast(pl.Utf8).str.zfill(6),
            ).alias("sampled_flow_id"),
            pl.col("packet_count").cast(pl.Int64).alias("sampled_packet_count"),
            pl.col("byte_count").cast(pl.Int64).alias("sampled_byte_count"),
            (pl.col("packet_count") * rate).cast(pl.Int64).alias("estimated_packet_count"),
            (pl.col("byte_count") * rate).cast(pl.Int64).alias("estimated_byte_count"),
        )
        .with_columns(
            pl.when(pl.col("duration_seconds") > 0)
            .then(pl.col("estimated_packet_count") / pl.col("duration_seconds"))
            .otherwise(None)
            .alias("sending_rate_packets_per_second"),
            pl.when(pl.col("duration_seconds") > 0)
            .then(pl.col("estimated_byte_count") / pl.col("duration_seconds"))
            .otherwise(None)
            .alias("sending_rate_bytes_per_second"),
        )
        .select(
            "dataset_id",
            "sampling_rate",
            "sampling_method",
            "random_seed",
            "sampled_flow_id",
            *config.methodology.flow_key_fields,
            "flow_sequence",
            "start_timestamp_us",
            "end_timestamp_us",
            "start_ts",
            "end_ts",
            "start_packet_index",
            "end_packet_index",
            "duration_seconds",
            "sampled_packet_count",
            "sampled_byte_count",
            "estimated_packet_count",
            "estimated_byte_count",
            "sending_rate_packets_per_second",
            "sending_rate_bytes_per_second",
            "size_basis",
            "byte_basis",
        )
    )


def _resolve_sampled_packets_path(config: PipelineConfig, sampled_packets_dir: Path, rate: int) -> Path:
    timeout_seconds = config.methodology.inactivity_timeout_seconds
    return sampled_packets_dir / f"{config.dataset.dataset_id}_{timeout_seconds}s_{rate}x_sampled_packets.parquet"


def _resolve_sampled_flows_path(config: PipelineConfig, sampled_flows_dir: Path, rate: int) -> Path:
    timeout_seconds = config.methodology.inactivity_timeout_seconds
    return sampled_flows_dir / f"{config.dataset.dataset_id}_{timeout_seconds}s_{rate}x_sampled_flows.parquet"


def _empty_sampled_flow_frame():
    import polars as pl

    return pl.DataFrame(
        schema={
            "dataset_id": pl.Utf8,
            "sampling_rate": pl.Int64,
            "sampling_method": pl.Utf8,
            "random_seed": pl.Int64,
            "sampled_flow_id": pl.Utf8,
            "src_ip": pl.Utf8,
            "dst_ip": pl.Utf8,
            "src_port": pl.Int32,
            "dst_port": pl.Int32,
            "protocol": pl.Utf8,
            "flow_sequence": pl.Int64,
            "start_timestamp_us": pl.Int64,
            "end_timestamp_us": pl.Int64,
            "start_ts": pl.Datetime(time_unit="us", time_zone="UTC"),
            "end_ts": pl.Datetime(time_unit="us", time_zone="UTC"),
            "start_packet_index": pl.Int64,
            "end_packet_index": pl.Int64,
            "duration_seconds": pl.Float64,
            "sampled_packet_count": pl.Int64,
            "sampled_byte_count": pl.Int64,
            "estimated_packet_count": pl.Int64,
            "estimated_byte_count": pl.Int64,
            "sending_rate_packets_per_second": pl.Float64,
            "sending_rate_bytes_per_second": pl.Float64,
            "size_basis": pl.Utf8,
            "byte_basis": pl.Utf8,
        }
    )
