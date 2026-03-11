"""Thin runtime helpers for the active dataset-root entrypoint."""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
import sys
from time import perf_counter

from .pipeline.driver import run_pipeline
from .shared.artifacts import build_artifact_paths
from .shared.config import DatasetConfig, OutputConfig, PipelineConfig, RuntimeConfig
from .shared.v2_config import DatasetTemplateConfig, ResolvedDatasetRun, RunConfig, resolve_dataset_runs


@dataclass(frozen=True)
class PlannedDatasetRun:
    """One dataset-scoped pipeline run planned from the active config surface."""

    resolved_run: ResolvedDatasetRun
    pipeline_config: PipelineConfig


def plan_active_runs(
    run_config: RunConfig,
    dataset_template: DatasetTemplateConfig,
) -> tuple[PlannedDatasetRun, ...]:
    """Resolve dataset-root execution into legacy-compatible pipeline configs."""

    resolved_runs = resolve_dataset_runs(run_config, dataset_template)
    return tuple(
        PlannedDatasetRun(
            resolved_run=resolved_run,
            pipeline_config=_to_pipeline_config(run_config, resolved_run),
        )
        for resolved_run in resolved_runs
    )


def render_active_plan(
    run_config: RunConfig,
    dataset_template: DatasetTemplateConfig,
) -> str:
    """Render the dataset-root execution plan for CLI output."""

    lines = [
        "Active pipeline plan",
        f"Datasets root: {run_config.paths.datasets_root}",
        f"Dataset glob: {dataset_template.dataset_glob}",
        f"Raw glob: {dataset_template.raw_glob}",
        f"Flow key: {', '.join(run_config.methodology.flow_key_fields)}",
        f"Inactivity timeout: {run_config.methodology.inactivity_timeout_seconds}s",
        f"Sampling rates: {', '.join(f'1:{rate}' for rate in run_config.sampling.normalized_rates())}",
        f"Sampling method: {run_config.sampling.method}",
        f"Size basis: {run_config.methodology.size_basis}",
        f"Byte basis: {run_config.methodology.byte_basis}",
        f"Plotting mode: {run_config.runtime.plotting_mode}",
        f"Cache policy: {run_config.runtime.cache_policy}",
        "",
    ]

    for planned_run in plan_active_runs(run_config, dataset_template):
        artifact_paths = build_artifact_paths(planned_run.pipeline_config)
        lines.extend(
            (
                f"[{planned_run.resolved_run.dataset_id}] {len(planned_run.resolved_run.capture_files)} capture files",
                f"  source dir -> {planned_run.resolved_run.dataset_dir}",
                f"  raw glob -> {planned_run.resolved_run.raw_glob}",
                f"  metric summary -> {artifact_paths.metric_summary}",
                f"  flow metrics -> {artifact_paths.flow_metrics}",
                f"  plots dir -> {artifact_paths.plots_dir}",
            )
        )

    return "\n".join(lines)


def run_active_runs(
    run_config: RunConfig,
    dataset_template: DatasetTemplateConfig,
    *,
    dry_run: bool = False,
) -> tuple[PlannedDatasetRun, ...]:
    """Execute dataset-root runs through the existing thin driver."""

    planned_runs = plan_active_runs(run_config, dataset_template)
    if dry_run:
        return planned_runs

    batch_start = perf_counter()
    _emit_runtime_event(f"[active] starting {len(planned_runs)} dataset runs")

    for run_index, planned_run in enumerate(planned_runs, start=1):
        dataset_start = perf_counter()
        dataset_id = planned_run.resolved_run.dataset_id
        _emit_runtime_event(
            f"[active] [{run_index}/{len(planned_runs)}] "
            f"{dataset_id} starting with {len(planned_run.resolved_run.capture_files)} capture files"
        )
        try:
            run_pipeline(planned_run.pipeline_config, dry_run=False)
        except BaseException:
            dataset_elapsed = perf_counter() - dataset_start
            _emit_runtime_event(
                f"[active] [{run_index}/{len(planned_runs)}] "
                f"{dataset_id} failed after {_format_elapsed(dataset_elapsed)}"
            )
            raise

        dataset_elapsed = perf_counter() - dataset_start
        _emit_runtime_event(
            f"[active] [{run_index}/{len(planned_runs)}] "
            f"{dataset_id} completed in {_format_elapsed(dataset_elapsed)}"
        )

    batch_elapsed = perf_counter() - batch_start
    _emit_runtime_event(f"[active] completed in {_format_elapsed(batch_elapsed)}")
    return planned_runs


def override_datasets_root(run_config: RunConfig, datasets_root: Path) -> RunConfig:
    """Return a copy of the run config with a datasets-root override applied."""

    return replace(
        run_config,
        paths=replace(run_config.paths, datasets_root=datasets_root.expanduser().resolve()),
    )


def _to_pipeline_config(run_config: RunConfig, resolved_run: ResolvedDatasetRun) -> PipelineConfig:
    workspace_root = run_config.paths.results_root.parent
    plotting_mode = run_config.runtime.plotting_mode.strip().lower()
    enable_plots = plotting_mode not in {"none", "off", "false", "disabled"}

    return PipelineConfig(
        config_path=run_config.config_path,
        dataset=DatasetConfig(
            dataset_id=resolved_run.dataset_id,
            input_dir=resolved_run.dataset_dir,
            raw_glob=resolved_run.raw_glob,
        ),
        output=OutputConfig(
            staged_dir=workspace_root / "data" / "staged",
            processed_dir=workspace_root / "data" / "processed",
            results_tables_dir=resolved_run.tables_dir,
            results_plots_dir=resolved_run.plots_dir,
        ),
        methodology=run_config.methodology,
        sampling=run_config.sampling,
        runtime=RuntimeConfig(
            workers=run_config.runtime.workers,
            enable_plots=enable_plots,
        ),
    )


def _emit_runtime_event(message: str) -> None:
    print(message, file=sys.stderr, flush=True)


def _format_elapsed(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.2f}s"

    minutes, remaining_seconds = divmod(seconds, 60)
    if minutes < 60:
        return f"{int(minutes)}m {remaining_seconds:05.2f}s"

    hours, remaining_minutes = divmod(int(minutes), 60)
    return f"{hours}h {remaining_minutes:02d}m {remaining_seconds:05.2f}s"
