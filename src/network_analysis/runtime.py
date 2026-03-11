"""Thin runtime helpers for the active dataset-root entrypoint."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import sys
from time import perf_counter
from typing import Callable

import yaml

from .pipeline.driver import ModuleRuntimeEvent, run_pipeline
from .shared.artifacts import build_artifact_paths
from .shared.config import DatasetConfig, OutputConfig, PipelineConfig, RuntimeConfig
from .shared.types import CachePolicy
from .shared.v2_config import DatasetTemplateConfig, ResolvedDatasetRun, RunConfig, resolve_dataset_runs


@dataclass(frozen=True)
class PlannedDatasetRun:
    """One dataset-scoped pipeline run planned from the active config surface."""

    resolved_run: ResolvedDatasetRun
    cache_layout: RuntimeCacheLayout
    pipeline_config: PipelineConfig


@dataclass(frozen=True)
class RuntimeCacheLayout:
    """Resolved cache roots for one active-architecture run."""

    policy: CachePolicy
    cache_root: Path
    staged_root: Path
    processed_root: Path


def plan_active_runs(
    run_config: RunConfig,
    dataset_template: DatasetTemplateConfig,
) -> tuple[PlannedDatasetRun, ...]:
    """Resolve dataset-root execution into legacy-compatible pipeline configs."""

    resolved_runs = resolve_dataset_runs(run_config, dataset_template)
    cache_layout = _resolve_cache_layout(run_config)
    return tuple(
        PlannedDatasetRun(
            resolved_run=resolved_run,
            cache_layout=cache_layout,
            pipeline_config=_to_pipeline_config(run_config, resolved_run, cache_layout),
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
        f"Cache root: {_resolve_cache_layout(run_config).cache_root}",
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
        run_started_at = datetime.now(timezone.utc)
        run_id = f"{dataset_id}-{run_started_at.strftime('%Y%m%dT%H%M%SZ')}"
        _prepare_runtime_artifacts(planned_run, run_config=run_config)
        log_path = planned_run.resolved_run.logs_dir / "run.log"
        stage_timings: dict[str, float] = {}
        _emit_runtime_event(
            f"[active] [{run_index}/{len(planned_runs)}] "
            f"{dataset_id} starting with {len(planned_run.resolved_run.capture_files)} capture files"
        )
        _append_log(
            log_path,
            f"[active] [{run_index}/{len(planned_runs)}] "
            f"{dataset_id} starting with {len(planned_run.resolved_run.capture_files)} capture files",
        )
        observer = _build_runtime_observer(log_path=log_path, stage_timings=stage_timings)
        try:
            run_pipeline(planned_run.pipeline_config, dry_run=False, observer=observer)
        except BaseException as exc:
            dataset_elapsed = perf_counter() - dataset_start
            _emit_runtime_event(
                f"[active] [{run_index}/{len(planned_runs)}] "
                f"{dataset_id} failed after {_format_elapsed(dataset_elapsed)}"
            )
            _append_log(
                log_path,
                f"[active] [{run_index}/{len(planned_runs)}] "
                f"{dataset_id} failed after {_format_elapsed(dataset_elapsed)}",
            )
            _write_runtime_manifest(
                planned_run,
                run_id=run_id,
                status="failed",
                started_at=run_started_at,
                finished_at=datetime.now(timezone.utc),
                stage_timings=stage_timings,
                error_message=str(exc),
            )
            raise

        dataset_elapsed = perf_counter() - dataset_start
        _emit_runtime_event(
            f"[active] [{run_index}/{len(planned_runs)}] "
            f"{dataset_id} completed in {_format_elapsed(dataset_elapsed)}"
        )
        _append_log(
            log_path,
            f"[active] [{run_index}/{len(planned_runs)}] "
            f"{dataset_id} completed in {_format_elapsed(dataset_elapsed)}",
        )
        _apply_cache_retention(planned_run)
        _write_runtime_manifest(
            planned_run,
            run_id=run_id,
            status="completed",
            started_at=run_started_at,
            finished_at=datetime.now(timezone.utc),
            stage_timings=stage_timings,
            error_message=None,
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


def _to_pipeline_config(
    run_config: RunConfig,
    resolved_run: ResolvedDatasetRun,
    cache_layout: RuntimeCacheLayout,
) -> PipelineConfig:
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
            staged_dir=cache_layout.staged_root,
            processed_dir=cache_layout.processed_root,
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


def _resolve_cache_layout(run_config: RunConfig) -> RuntimeCacheLayout:
    cache_root = (
        run_config.paths.results_root.parent
        / ".cache"
        / "network_analysis"
        / run_config.runtime.cache_policy.value
    )
    return RuntimeCacheLayout(
        policy=run_config.runtime.cache_policy,
        cache_root=cache_root,
        staged_root=cache_root / "staged",
        processed_root=cache_root / "processed",
    )


def _prepare_runtime_artifacts(planned_run: PlannedDatasetRun, *, run_config: RunConfig) -> None:
    planned_run.resolved_run.meta_dir.mkdir(parents=True, exist_ok=True)
    planned_run.resolved_run.logs_dir.mkdir(parents=True, exist_ok=True)

    resolved_dataset_snapshot = {
        "dataset_id": planned_run.resolved_run.dataset_id,
        "dataset_dir": str(planned_run.resolved_run.dataset_dir),
        "raw_glob": planned_run.resolved_run.raw_glob,
        "capture_files": [str(path) for path in planned_run.resolved_run.capture_files],
        "results_root": str(planned_run.resolved_run.results_root),
    }
    (planned_run.resolved_run.meta_dir / "resolved_dataset.yaml").write_text(
        yaml.safe_dump(resolved_dataset_snapshot, sort_keys=False),
        encoding="utf-8",
    )

    run_config_snapshot = {
        "run_config_path": str(run_config.config_path),
        "datasets_root": str(run_config.paths.datasets_root),
        "results_root": str(run_config.paths.results_root),
        "methodology": {
            "flow_key_fields": list(run_config.methodology.flow_key_fields),
            "inactivity_timeout_seconds": run_config.methodology.inactivity_timeout_seconds,
            "size_basis": run_config.methodology.size_basis.value,
            "byte_basis": run_config.methodology.byte_basis.value,
        },
        "sampling": {
            "rates": list(run_config.sampling.rates),
            "normalized_rates": list(run_config.sampling.normalized_rates()),
            "method": run_config.sampling.method.value,
            "random_seed": run_config.sampling.random_seed,
        },
        "runtime": {
            "plotting_mode": run_config.runtime.plotting_mode,
            "cache_policy": run_config.runtime.cache_policy.value,
            "workers": run_config.runtime.workers,
            "logging": {"level": run_config.runtime.logging.level},
        },
    }
    (planned_run.resolved_run.meta_dir / "run_config.yaml").write_text(
        yaml.safe_dump(run_config_snapshot, sort_keys=False),
        encoding="utf-8",
    )


def _apply_cache_retention(planned_run: PlannedDatasetRun) -> None:
    artifact_paths = build_artifact_paths(planned_run.pipeline_config)

    if planned_run.cache_layout.policy == CachePolicy.DEBUG:
        return

    _remove_tree_if_present(artifact_paths.staged_dir)
    if planned_run.cache_layout.policy == CachePolicy.NONE:
        _remove_tree_if_present(artifact_paths.processed_dir)


def _build_runtime_observer(
    *,
    log_path: Path,
    stage_timings: dict[str, float],
) -> Callable[[ModuleRuntimeEvent], None]:
    def observer(event: ModuleRuntimeEvent) -> None:
        if event.status == "starting":
            message = (
                f"[dataset {event.dataset_id}] [{event.module_index}/{event.module_total}] "
                f"{event.module_name} starting"
            )
        else:
            elapsed = _format_elapsed(event.elapsed_seconds or 0.0)
            message = (
                f"[dataset {event.dataset_id}] [{event.module_index}/{event.module_total}] "
                f"{event.module_name} {event.status} in {elapsed}"
            )
            stage_timings[event.module_name] = event.elapsed_seconds or 0.0

        _emit_runtime_event(message)
        _append_log(log_path, message)

    return observer


def _write_runtime_manifest(
    planned_run: PlannedDatasetRun,
    *,
    run_id: str,
    status: str,
    started_at: datetime,
    finished_at: datetime,
    stage_timings: dict[str, float],
    error_message: str | None,
) -> None:
    artifact_paths = build_artifact_paths(planned_run.pipeline_config)
    stage_timings_path = planned_run.resolved_run.meta_dir / "stage_timings.json"
    stage_timings_path.write_text(
        json.dumps(stage_timings, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    manifest = {
        "run_id": run_id,
        "dataset_id": planned_run.resolved_run.dataset_id,
        "status": status,
        "started_at": started_at.isoformat(),
        "finished_at": finished_at.isoformat(),
        "capture_files": [str(path) for path in planned_run.resolved_run.capture_files],
        "stage_timings_path": str(stage_timings_path),
        "outputs": {
            "meta_dir": str(planned_run.resolved_run.meta_dir),
            "tables_dir": str(planned_run.resolved_run.tables_dir),
            "plots_dir": str(artifact_paths.plots_dir),
            "logs_dir": str(planned_run.resolved_run.logs_dir),
            "metric_summary": str(artifact_paths.metric_summary),
            "flow_metrics": str(artifact_paths.flow_metrics),
        },
        "cache": {
            "policy": planned_run.cache_layout.policy.value,
            "root": str(planned_run.cache_layout.cache_root),
            "staged_dir": str(artifact_paths.staged_dir),
            "processed_dir": str(artifact_paths.processed_dir),
            "staged_dir_exists": artifact_paths.staged_dir.exists(),
            "processed_dir_exists": artifact_paths.processed_dir.exists(),
            "sampled_packets_dir_exists": artifact_paths.sampled_packets_dir.exists(),
            "sampled_flows_dir_exists": artifact_paths.sampled_flows_dir.exists(),
        },
        "error_message": error_message,
    }
    (planned_run.resolved_run.meta_dir / "run_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _remove_tree_if_present(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)


def _append_log(log_path: Path, message: str) -> None:
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(message + "\n")
