"""Helpers for resolving dataset-specific artifact paths."""

from dataclasses import dataclass
from pathlib import Path

from .config import PipelineConfig


@dataclass(frozen=True)
class DatasetArtifactPaths:
    """Absolute artifact paths for a configured dataset."""

    dataset_id: str
    staged_dir: Path
    processed_dir: Path
    results_tables_dir: Path
    results_plots_dir: Path
    dataset_registry: Path
    ingest_manifest: Path
    packets: Path
    packet_extraction_manifest: Path
    baseline_flows: Path
    sampled_flows_dir: Path
    sampling_manifest: Path
    metric_summary: Path
    flow_metrics: Path
    plots_dir: Path


def build_artifact_paths(config: PipelineConfig) -> DatasetArtifactPaths:
    """Build absolute artifact paths from the configured output roots."""

    dataset_id = config.dataset.dataset_id
    staged_dir = config.output.staged_dir / dataset_id
    processed_dir = config.output.processed_dir / dataset_id
    plots_dir = config.output.results_plots_dir / dataset_id

    return DatasetArtifactPaths(
        dataset_id=dataset_id,
        staged_dir=staged_dir,
        processed_dir=processed_dir,
        results_tables_dir=config.output.results_tables_dir,
        results_plots_dir=config.output.results_plots_dir,
        dataset_registry=processed_dir / "dataset_registry.parquet",
        ingest_manifest=processed_dir / "ingest_manifest.parquet",
        packets=processed_dir / "packets.parquet",
        packet_extraction_manifest=processed_dir / "packet_extraction_manifest.parquet",
        baseline_flows=processed_dir / "baseline_flows.parquet",
        sampled_flows_dir=processed_dir / "sampled_flows",
        sampling_manifest=processed_dir / "sampling_runs.parquet",
        metric_summary=config.output.results_tables_dir / f"{dataset_id}_metric_summary.parquet",
        flow_metrics=config.output.results_tables_dir / f"{dataset_id}_flow_metrics.parquet",
        plots_dir=plots_dir,
    )
