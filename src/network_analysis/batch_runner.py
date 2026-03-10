"""Batch runner that discovers dataset folders and invokes the single-dataset pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from .pipeline.driver import run_pipeline
from .shared.batch_config import BatchConfig
from .shared.config import DatasetConfig, OutputConfig, PipelineConfig
from .shared.artifacts import build_artifact_paths
from .modules.dataset_registry import infer_capture_details


@dataclass(frozen=True)
class PlannedBatchRun:
    """A single capture-file analysis derived from a dataset-folder batch config."""

    dataset_name: str
    category: str
    run_id: str
    source_file: Path
    pipeline_config: PipelineConfig


def plan_batch_runs(config: BatchConfig) -> tuple[PlannedBatchRun, ...]:
    """Resolve capture-file batch runs from the configured datasets root."""

    dataset_dirs = _discover_dataset_dirs(config)
    planned_runs: list[PlannedBatchRun] = []
    category_pattern = config.categorization.compiled_pattern()

    for dataset_dir in dataset_dirs:
        capture_files = _discover_capture_files(dataset_dir)
        for source_file in capture_files:
            category = infer_capture_category(
                source_file,
                category_pattern=category_pattern,
                default_category=config.categorization.default_category,
            )
            run_id = _derive_run_id(source_file)
            pipeline_config = PipelineConfig(
                config_path=config.config_path,
                dataset=DatasetConfig(
                    dataset_id=run_id,
                    input_dir=source_file.parent,
                    raw_glob=source_file.name,
                ),
                output=OutputConfig(
                    staged_dir=config.output.staged_root / dataset_dir.name / category,
                    processed_dir=config.output.processed_root / dataset_dir.name / category,
                    results_tables_dir=config.output.results_root / dataset_dir.name / category / "tables",
                    results_plots_dir=config.output.results_root / dataset_dir.name / category / "plots",
                ),
                methodology=config.methodology,
                sampling=config.sampling,
                runtime=config.runtime,
            )
            planned_runs.append(
                PlannedBatchRun(
                    dataset_name=dataset_dir.name,
                    category=category,
                    run_id=run_id,
                    source_file=source_file,
                    pipeline_config=pipeline_config,
                )
            )

    if not planned_runs:
        raise FileNotFoundError(
            f"No supported capture files were found under dataset subfolders in {config.discovery.datasets_root}"
        )

    return tuple(
        sorted(
            planned_runs,
            key=lambda run: (
                _natural_sort_key(run.dataset_name),
                _natural_sort_key(run.category),
                _natural_sort_key(run.source_file.name),
            ),
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
                f"[{run.dataset_name}/{run.category}] {run.source_file.name}",
                f"  run id -> {run.run_id}",
                f"  source -> {run.source_file}",
                f"  metric summary -> {artifact_paths.metric_summary}",
                f"  flow metrics -> {artifact_paths.flow_metrics}",
                f"  plots dir -> {artifact_paths.plots_dir}",
            )
        )

    return "\n".join(lines)


def run_batch(config: BatchConfig, *, dry_run: bool = False) -> tuple[PlannedBatchRun, ...]:
    """Run the existing single-dataset pipeline once per discovered capture file."""

    planned_runs = plan_batch_runs(config)
    if dry_run:
        return planned_runs

    for planned_run in planned_runs:
        run_pipeline(planned_run.pipeline_config, dry_run=False)

    return planned_runs


def infer_capture_category(
    source_file: Path,
    *,
    category_pattern: re.Pattern[str],
    default_category: str,
) -> str:
    """Infer a traffic category from the capture filename."""

    match = category_pattern.match(_strip_known_suffixes(source_file.name))
    if not match:
        return default_category

    category = match.groupdict().get("category")
    if category is None or not category.strip():
        return default_category
    return category.strip()


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
        (candidate for candidate in dataset_dir.rglob("*") if candidate.is_file()),
        key=lambda candidate: _natural_sort_key(str(candidate.relative_to(dataset_dir))),
    ):
        try:
            infer_capture_details(path)
        except ValueError:
            continue
        capture_files.append(path)
    return tuple(capture_files)


def _derive_run_id(source_file: Path) -> str:
    stem = _strip_known_suffixes(source_file.name)
    return _slugify(stem)


def _strip_known_suffixes(filename: str) -> str:
    path = Path(filename)
    suffixes = [suffix.lower() for suffix in path.suffixes]
    known_suffixes = {".pcap", ".pcapng", ".gz", ".xz", ".zip", ".rar"}
    stem = path.name
    while True:
        suffix = Path(stem).suffix.lower()
        if not suffix or suffix not in known_suffixes:
            return stem
        stem = stem[: -len(suffix)]


def _slugify(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._-")
    return slug or "capture_run"


def _natural_sort_key(value: str) -> tuple[object, ...]:
    return tuple(
        int(part) if part.isdigit() else part.lower()
        for part in re.split(r"(\d+)", value)
    )
