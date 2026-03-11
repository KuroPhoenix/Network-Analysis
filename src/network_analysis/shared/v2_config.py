"""Configuration loading and dataset resolution for the active v2 architecture."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from ..modules.dataset_registry import infer_capture_details
from .config import (
    ConfigError,
    MethodologyConfig,
    SamplingConfig,
    _get_section,
    _optional_int,
    _optional_string,
    _parse_byte_basis,
    _parse_flow_key,
    _parse_sampling_method,
    _parse_sampling_rates,
    _parse_size_basis,
    _require_non_empty_string,
    _require_positive_int,
    _resolve_path,
)
from .constants import (
    DEFAULT_BYTE_BASIS,
    DEFAULT_FLOW_KEY_FIELDS,
    DEFAULT_INACTIVITY_TIMEOUT_SECONDS,
    DEFAULT_SAMPLING_METHOD,
    DEFAULT_SAMPLING_RATES,
    DEFAULT_SIZE_BASIS,
)
from .types import CachePolicy

DEFAULT_DATASET_GLOB = "*"
DEFAULT_RAW_GLOB = "*.pcap*"
DEFAULT_PLOTTING_MODE = "minimal"
DEFAULT_LOG_LEVEL = "INFO"


class V2ConfigError(ConfigError):
    """Raised when active-architecture config content is invalid."""


@dataclass(frozen=True)
class DatasetTemplateConfig:
    """Dataset discovery defaults for the active architecture."""

    config_path: Path
    dataset_glob: str = DEFAULT_DATASET_GLOB
    raw_glob: str = DEFAULT_RAW_GLOB

    def summary_lines(self) -> tuple[str, ...]:
        """Render a concise summary for validation output."""

        return (
            f"Dataset template: {self.config_path}",
            f"Dataset glob: {self.dataset_glob}",
            f"Raw glob: {self.raw_glob}",
        )


@dataclass(frozen=True)
class LoggingConfig:
    """Logging settings carried by the active run config."""

    level: str = DEFAULT_LOG_LEVEL


@dataclass(frozen=True)
class RunPathConfig:
    """Input and output roots for the active architecture."""

    datasets_root: Path
    results_root: Path


@dataclass(frozen=True)
class V2RuntimeConfig:
    """Runtime controls for the active architecture."""

    plotting_mode: str = DEFAULT_PLOTTING_MODE
    cache_policy: CachePolicy = CachePolicy.MINIMAL
    workers: int = 1
    logging: LoggingConfig = field(default_factory=LoggingConfig)


@dataclass(frozen=True)
class RunConfig:
    """Top-level active-architecture run config."""

    config_path: Path
    paths: RunPathConfig
    methodology: MethodologyConfig
    sampling: SamplingConfig
    runtime: V2RuntimeConfig

    def summary_lines(self) -> tuple[str, ...]:
        """Render a concise summary for validation output."""

        return (
            f"Run config: {self.config_path}",
            f"Datasets root: {self.paths.datasets_root}",
            f"Results root: {self.paths.results_root}",
            f"Flow key: {', '.join(self.methodology.flow_key_fields)}",
            f"Inactivity timeout: {self.methodology.inactivity_timeout_seconds}s",
            f"Sampling rates: {', '.join(f'1:{rate}' for rate in self.sampling.normalized_rates())}",
            f"Sampling method: {self.sampling.method}",
            f"Size basis: {self.methodology.size_basis}",
            f"Byte basis: {self.methodology.byte_basis}",
            f"Plotting mode: {self.runtime.plotting_mode}",
            f"Cache policy: {self.runtime.cache_policy}",
            f"Workers: {self.runtime.workers}",
            f"Log level: {self.runtime.logging.level}",
        )


@dataclass(frozen=True)
class ResolvedDatasetRun:
    """One dataset-scoped run derived from the active architecture config surface."""

    dataset_id: str
    dataset_dir: Path
    raw_glob: str
    capture_files: tuple[Path, ...]
    results_root: Path

    @property
    def dataset_results_dir(self) -> Path:
        return self.results_root / self.dataset_id

    @property
    def meta_dir(self) -> Path:
        return self.dataset_results_dir / "meta"

    @property
    def tables_dir(self) -> Path:
        return self.dataset_results_dir / "tables"

    @property
    def plots_dir(self) -> Path:
        return self.dataset_results_dir / "plots"

    @property
    def logs_dir(self) -> Path:
        return self.dataset_results_dir / "logs"


def load_dataset_template(path: str | Path) -> DatasetTemplateConfig:
    """Load dataset discovery defaults for the active architecture."""

    config_path, raw_data = _load_yaml_mapping(path)
    discovery_data = _get_section(raw_data, "discovery", required=False)

    return DatasetTemplateConfig(
        config_path=config_path,
        dataset_glob=_optional_string(
            discovery_data.get("dataset_glob"),
            "discovery.dataset_glob",
            default=DEFAULT_DATASET_GLOB,
        ),
        raw_glob=_optional_string(
            discovery_data.get("raw_glob"),
            "discovery.raw_glob",
            default=DEFAULT_RAW_GLOB,
        ),
    )


def load_run_config(path: str | Path) -> RunConfig:
    """Load the active-architecture run config."""

    config_path, raw_data = _load_yaml_mapping(path)
    base_dir = config_path.parent
    input_data = _get_section(raw_data, "input")
    output_data = _get_section(raw_data, "output")
    methodology_data = _get_section(raw_data, "methodology", required=False)
    sampling_data = _get_section(raw_data, "sampling", required=False)
    runtime_data = _get_section(raw_data, "runtime", required=False)
    logging_data = _get_section(runtime_data, "logging", required=False)

    return RunConfig(
        config_path=config_path,
        paths=RunPathConfig(
            datasets_root=_resolve_path(
                _require_non_empty_string(input_data.get("datasets_root"), "input.datasets_root"),
                base_dir,
            ),
            results_root=_resolve_path(
                _require_non_empty_string(output_data.get("results_root"), "output.results_root"),
                base_dir,
            ),
        ),
        methodology=MethodologyConfig(
            flow_key_fields=_parse_flow_key(methodology_data.get("flow_key_fields", DEFAULT_FLOW_KEY_FIELDS)),
            inactivity_timeout_seconds=_require_positive_int(
                methodology_data.get(
                    "inactivity_timeout_seconds",
                    DEFAULT_INACTIVITY_TIMEOUT_SECONDS,
                ),
                "methodology.inactivity_timeout_seconds",
            ),
            size_basis=_parse_size_basis(methodology_data.get("size_basis", DEFAULT_SIZE_BASIS)),
            byte_basis=_parse_byte_basis(methodology_data.get("byte_basis", DEFAULT_BYTE_BASIS)),
        ),
        sampling=SamplingConfig(
            rates=_parse_sampling_rates(sampling_data.get("rates", DEFAULT_SAMPLING_RATES)),
            method=_parse_sampling_method(sampling_data.get("method", DEFAULT_SAMPLING_METHOD)),
            random_seed=_optional_int(sampling_data.get("random_seed"), "sampling.random_seed"),
        ),
        runtime=V2RuntimeConfig(
            plotting_mode=_optional_string(
                runtime_data.get("plotting_mode"),
                "runtime.plotting_mode",
                default=DEFAULT_PLOTTING_MODE,
            ),
            cache_policy=_parse_cache_policy(runtime_data.get("cache_policy", CachePolicy.MINIMAL.value)),
            workers=_require_positive_int(runtime_data.get("workers", 1), "runtime.workers"),
            logging=LoggingConfig(
                level=_optional_string(
                    logging_data.get("level"),
                    "runtime.logging.level",
                    default=DEFAULT_LOG_LEVEL,
                )
            ),
        ),
    )


def resolve_dataset_runs(
    run_config: RunConfig,
    dataset_template: DatasetTemplateConfig,
) -> tuple[ResolvedDatasetRun, ...]:
    """Resolve one dataset-scoped run per discovered dataset directory."""

    datasets_root = run_config.paths.datasets_root
    if not datasets_root.exists():
        raise FileNotFoundError(f"Configured datasets root does not exist: {datasets_root}")
    if not datasets_root.is_dir():
        raise NotADirectoryError(f"Configured datasets root is not a directory: {datasets_root}")

    dataset_dirs = tuple(
        sorted(
            (
                path
                for path in datasets_root.glob(dataset_template.dataset_glob)
                if path.is_dir()
            ),
            key=lambda path: path.name.lower(),
        )
    )
    if not dataset_dirs:
        raise FileNotFoundError(
            f"No dataset directories matched {dataset_template.dataset_glob!r} under {datasets_root}"
        )

    resolved_runs: list[ResolvedDatasetRun] = []
    for dataset_dir in dataset_dirs:
        capture_files = tuple(
            path
            for path in sorted(dataset_dir.glob(dataset_template.raw_glob), key=lambda candidate: candidate.name.lower())
            if path.is_file() and _is_supported_capture(candidate=path)
        )
        if not capture_files:
            raise FileNotFoundError(
                f"No supported capture files matched {dataset_template.raw_glob!r} under {dataset_dir}"
            )

        resolved_runs.append(
            ResolvedDatasetRun(
                dataset_id=dataset_dir.name,
                dataset_dir=dataset_dir,
                raw_glob=dataset_template.raw_glob,
                capture_files=capture_files,
                results_root=run_config.paths.results_root,
            )
        )

    return tuple(resolved_runs)


def _load_yaml_mapping(path: str | Path) -> tuple[Path, dict[str, Any]]:
    config_path = Path(path).expanduser().resolve()
    raw_data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw_data, dict):
        raise V2ConfigError("Top-level config must be a mapping.")
    return config_path, raw_data


def _is_supported_capture(*, candidate: Path) -> bool:
    try:
        infer_capture_details(candidate)
    except ValueError:
        return False
    return True


def _parse_cache_policy(value: Any) -> CachePolicy:
    try:
        return CachePolicy(str(value))
    except ValueError as exc:
        raise V2ConfigError("runtime.cache_policy must be one of: none, minimal, debug.") from exc
