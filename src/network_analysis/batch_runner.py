"""Batch runner that discovers dataset folders and invokes the single-dataset pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import shutil
from time import perf_counter

from .modules.dataset_registry import infer_capture_details
from .pipeline.driver import run_pipeline
from .shared.artifacts import build_artifact_paths
from .shared.batch_config import BatchConfig
from .shared.config import DatasetConfig, OutputConfig, PipelineConfig
from .shared.runtime_feedback import emit_runtime_event, format_elapsed, progress_bar

BATCH_CAPTURE_GLOB = "*.pcap*"


@dataclass(frozen=True)
class PlannedBatchRun:
    """A single dataset-folder analysis derived from a batch config."""

    dataset_name: str
    run_id: str
    source_dir: Path
    capture_files: tuple[Path, ...]
    pipeline_config: PipelineConfig


@dataclass(frozen=True)
class BatchCleanupSummary:
    """Cleanup details for one dataset-folder run."""

    dataset_name: str
    run_id: str
    removed_paths: tuple[Path, ...]


def plan_batch_runs(config: BatchConfig) -> tuple[PlannedBatchRun, ...]:
    """Resolve one dataset-folder run per configured dataset directory."""

    dataset_dirs = _discover_dataset_dirs(config)
    planned_runs: list[PlannedBatchRun] = []

    for dataset_dir in dataset_dirs:
        capture_files = _discover_capture_files(dataset_dir)
        if not capture_files:
            raise FileNotFoundError(
                f"No supported capture files were found directly under dataset folder {dataset_dir}"
            )

        run_id = _derive_run_id(dataset_dir)
        pipeline_config = PipelineConfig(
            config_path=config.config_path,
            dataset=DatasetConfig(
                dataset_id=run_id,
                input_dir=dataset_dir,
                raw_glob=BATCH_CAPTURE_GLOB,
            ),
            output=OutputConfig(
                staged_dir=config.output.staged_root,
                processed_dir=config.output.processed_root,
                results_tables_dir=config.output.results_root / dataset_dir.name / "tables",
                results_plots_dir=config.output.results_root / dataset_dir.name / "plots",
            ),
            methodology=config.methodology,
            sampling=config.sampling,
            runtime=config.runtime,
        )
        planned_runs.append(
            PlannedBatchRun(
                dataset_name=dataset_dir.name,
                run_id=run_id,
                source_dir=dataset_dir,
                capture_files=capture_files,
                pipeline_config=pipeline_config,
            )
        )

    if not planned_runs:
        raise FileNotFoundError(
            f"No dataset subfolders with supported capture files were found under {config.discovery.datasets_root}"
        )

    return tuple(
        sorted(
            planned_runs,
            key=lambda run: _natural_sort_key(run.dataset_name),
        )
    )


def render_batch_plan(config: BatchConfig) -> str:
    """Render the resolved batch plan for CLI output."""

    lines = [
        "Batch pipeline plan",
        f"Datasets root: {config.discovery.datasets_root}",
        f"Dataset glob: {config.discovery.dataset_glob}",
        f"Flow key: {', '.join(config.methodology.flow_key_fields)}",
        f"Inactivity timeout: {config.methodology.inactivity_timeout_seconds}s",
        f"Sampling rates: {', '.join(f'1:{rate}' for rate in config.sampling.normalized_rates())}",
        f"Plots enabled: {config.runtime.enable_plots}",
        "",
    ]

    for run in plan_batch_runs(config):
        artifact_paths = build_artifact_paths(run.pipeline_config)
        lines.extend(
            (
                f"[{run.dataset_name}] {len(run.capture_files)} capture files",
                f"  run id -> {run.run_id}",
                f"  source dir -> {run.source_dir}",
                f"  raw glob -> {run.pipeline_config.dataset.raw_glob}",
                f"  metric summary -> {artifact_paths.metric_summary}",
                f"  flow metrics -> {artifact_paths.flow_metrics}",
                f"  plots dir -> {artifact_paths.plots_dir}",
            )
        )

    return "\n".join(lines)


def run_batch(config: BatchConfig, *, dry_run: bool = False) -> tuple[PlannedBatchRun, ...]:
    """Run the existing single-dataset pipeline once per discovered dataset folder."""

    planned_runs = plan_batch_runs(config)
    if dry_run:
        return planned_runs

    batch_start = perf_counter()
    emit_runtime_event(f"[batch] starting {len(planned_runs)} dataset runs")

    with progress_bar(
        total=len(planned_runs),
        desc="batch datasets",
        unit="dataset",
        leave=True,
    ) as bar:
        for run_index, planned_run in enumerate(planned_runs, start=1):
            dataset_start = perf_counter()
            emit_runtime_event(
                f"[batch] [{run_index}/{len(planned_runs)}] "
                f"{planned_run.run_id} starting with {len(planned_run.capture_files)} capture files"
            )
            try:
                run_pipeline(planned_run.pipeline_config, dry_run=False)
            except BaseException:
                dataset_elapsed = perf_counter() - dataset_start
                emit_runtime_event(
                    f"[batch] [{run_index}/{len(planned_runs)}] "
                    f"{planned_run.run_id} failed after {format_elapsed(dataset_elapsed)}"
                )
                raise

            bar.update(1)
            dataset_elapsed = perf_counter() - dataset_start
            emit_runtime_event(
                f"[batch] [{run_index}/{len(planned_runs)}] "
                f"{planned_run.run_id} completed in {format_elapsed(dataset_elapsed)}"
            )

    batch_elapsed = perf_counter() - batch_start
    emit_runtime_event(f"[batch] completed in {format_elapsed(batch_elapsed)}")

    return planned_runs


def clean_batch_outputs(config: BatchConfig) -> tuple[BatchCleanupSummary, ...]:
    """Remove reproducible generated artifacts for the planned dataset runs."""

    cleanup_summaries: list[BatchCleanupSummary] = []
    for planned_run in plan_batch_runs(config):
        artifact_paths = build_artifact_paths(planned_run.pipeline_config)
        removable_paths = (
            artifact_paths.staged_dir,
            artifact_paths.processed_dir,
            artifact_paths.results_tables_dir,
            artifact_paths.results_plots_dir,
        )
        removed_paths: list[Path] = []
        for path in removable_paths:
            if path.exists():
                shutil.rmtree(path)
                removed_paths.append(path)

        dataset_results_root = artifact_paths.results_tables_dir.parent
        if dataset_results_root.exists() and not any(dataset_results_root.iterdir()):
            dataset_results_root.rmdir()

        cleanup_summaries.append(
            BatchCleanupSummary(
                dataset_name=planned_run.dataset_name,
                run_id=planned_run.run_id,
                removed_paths=tuple(removed_paths),
            )
        )

    return tuple(cleanup_summaries)


def _discover_dataset_dirs(config: BatchConfig) -> tuple[Path, ...]:
    datasets_root = config.discovery.datasets_root
    if not datasets_root.exists():
        raise FileNotFoundError(f"Configured datasets root does not exist: {datasets_root}")
    if not datasets_root.is_dir():
        raise NotADirectoryError(f"Configured datasets root is not a directory: {datasets_root}")

    dataset_dirs = tuple(
        sorted(
            (
                path
                for path in datasets_root.glob(config.discovery.dataset_glob)
                if path.is_dir()
            ),
            key=lambda path: _natural_sort_key(path.name),
        )
    )
    if not dataset_dirs:
        raise FileNotFoundError(
            f"No dataset subfolders matched {config.discovery.dataset_glob!r} under {datasets_root}"
        )
    return dataset_dirs


def _discover_capture_files(dataset_dir: Path) -> tuple[Path, ...]:
    capture_files: list[Path] = []
    for path in sorted(
        (
            candidate
            for candidate in dataset_dir.glob(BATCH_CAPTURE_GLOB)
            if candidate.is_file()
        ),
        key=lambda candidate: _natural_sort_key(candidate.name),
    ):
        try:
            infer_capture_details(path)
        except ValueError:
            continue
        capture_files.append(path)
    return tuple(capture_files)


def _derive_run_id(dataset_dir: Path) -> str:
    return _slugify(dataset_dir.name)


def _slugify(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._-")
    return slug or "capture_run"


def _natural_sort_key(value: str) -> tuple[object, ...]:
    return tuple(
        int(part) if part.isdigit() else part.lower()
        for part in re.split(r"(\d+)", value)
    )
