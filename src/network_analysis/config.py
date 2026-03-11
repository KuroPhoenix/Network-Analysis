"""Active configuration and dataset-resolution model for the pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .constants import (
    DEFAULT_BYTE_BASIS,
    DEFAULT_FLOW_KEY_FIELDS,
    DEFAULT_INACTIVITY_TIMEOUT_SECONDS,
    DEFAULT_SAMPLING_METHOD,
    DEFAULT_SAMPLING_RATES,
    DEFAULT_SIZE_BASIS,
)
from .types import ByteBasis, CachePolicy, CaptureFormat, CompressionType, SamplingMethod, SizeBasis

DEFAULT_DATASET_GLOB = "*"
DEFAULT_RAW_GLOB = "*.pcap*"
DEFAULT_PLOTTING_MODE = "minimal"
DEFAULT_LOG_LEVEL = "INFO"


class ConfigError(ValueError):
    """Raised when configuration content is invalid."""


class V2ConfigError(ConfigError):
    """Raised when active-architecture config content is invalid."""


@dataclass(frozen=True)
class DatasetConfig:
    """Dataset discovery settings for one dataset-scoped run."""

    dataset_id: str
    input_dir: Path
    raw_glob: str = DEFAULT_RAW_GLOB


@dataclass(frozen=True)
class OutputConfig:
    """Repository output locations used by pipeline modules."""

    staged_dir: Path
    processed_dir: Path
    results_tables_dir: Path
    results_plots_dir: Path


@dataclass(frozen=True)
class MethodologyConfig:
    """Methodology choices that must remain explicit and reproducible."""

    flow_key_fields: tuple[str, ...] = DEFAULT_FLOW_KEY_FIELDS
    inactivity_timeout_seconds: int = DEFAULT_INACTIVITY_TIMEOUT_SECONDS
    size_basis: SizeBasis = SizeBasis(DEFAULT_SIZE_BASIS)
    byte_basis: ByteBasis = ByteBasis(DEFAULT_BYTE_BASIS)

    def requested_size_bases(self) -> tuple[SizeBasis, ...]:
        """Return the concrete size bases that downstream modules should compute."""

        if self.size_basis == SizeBasis.BOTH:
            return (SizeBasis.PACKETS, SizeBasis.BYTES)
        return (self.size_basis,)


@dataclass(frozen=True)
class SamplingConfig:
    """Sampling settings used by later pipeline modules."""

    rates: tuple[int, ...] = DEFAULT_SAMPLING_RATES
    method: SamplingMethod = SamplingMethod(DEFAULT_SAMPLING_METHOD)
    random_seed: int | None = None

    def normalized_rates(self) -> tuple[int, ...]:
        """Return configured sampling rates with the mandatory 1:1 baseline."""

        return tuple(dict.fromkeys((1, *self.rates)))


@dataclass(frozen=True)
class LoggingConfig:
    """Logging settings carried by the active runtime config."""

    level: str = DEFAULT_LOG_LEVEL


@dataclass(frozen=True)
class RuntimeConfig:
    """Runtime controls for the active architecture."""

    plotting_mode: str = DEFAULT_PLOTTING_MODE
    cache_policy: CachePolicy = CachePolicy.MINIMAL
    workers: int = 1
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    def plots_enabled(self) -> bool:
        """Return whether the configured plotting mode requests plot rendering."""

        return self.plotting_mode.strip().lower() not in {"none", "off", "false", "disabled"}


@dataclass(frozen=True)
class RunPathConfig:
    """Input and output roots for the active architecture."""

    datasets_root: Path
    results_root: Path


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
class RunConfig:
    """Top-level active-architecture run config."""

    config_path: Path
    paths: RunPathConfig
    methodology: MethodologyConfig
    sampling: SamplingConfig
    runtime: RuntimeConfig

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


@dataclass(frozen=True)
class DatasetRunConfig:
    """Resolved per-dataset execution config for the active architecture."""

    config_path: Path
    dataset: DatasetConfig
    output: OutputConfig
    methodology: MethodologyConfig
    sampling: SamplingConfig
    runtime: RuntimeConfig

    def summary_lines(self) -> tuple[str, ...]:
        """Render a concise summary for validation output."""

        return (
            f"Run config: {self.config_path}",
            f"Dataset: {self.dataset.dataset_id}",
            f"Input dir: {self.dataset.input_dir}",
            f"Flow key: {', '.join(self.methodology.flow_key_fields)}",
            f"Inactivity timeout: {self.methodology.inactivity_timeout_seconds}s",
            f"Sampling rates: {', '.join(f'1:{rate}' for rate in self.sampling.normalized_rates())}",
            f"Sampling method: {self.sampling.method}",
            f"Size basis: {self.methodology.size_basis}",
            f"Byte basis: {self.methodology.byte_basis}",
            f"Staged dir: {self.output.staged_dir}",
            f"Processed dir: {self.output.processed_dir}",
            f"Results tables dir: {self.output.results_tables_dir}",
            f"Results plots dir: {self.output.results_plots_dir}",
            f"Workers: {self.runtime.workers}",
            f"Plotting mode: {self.runtime.plotting_mode}",
            f"Cache policy: {self.runtime.cache_policy}",
        )


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
        runtime=RuntimeConfig(
            plotting_mode=_parse_plotting_mode(
                runtime_data.get("plotting_mode", DEFAULT_PLOTTING_MODE)
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


def build_dataset_run_config(
    run_config: RunConfig,
    resolved_run: ResolvedDatasetRun,
    *,
    staged_root: Path,
    processed_root: Path,
) -> DatasetRunConfig:
    """Build one per-dataset executable config from the active runtime model."""

    return DatasetRunConfig(
        config_path=run_config.config_path,
        dataset=DatasetConfig(
            dataset_id=resolved_run.dataset_id,
            input_dir=resolved_run.dataset_dir,
            raw_glob=resolved_run.raw_glob,
        ),
        output=OutputConfig(
            staged_dir=staged_root,
            processed_dir=processed_root,
            results_tables_dir=resolved_run.tables_dir,
            results_plots_dir=resolved_run.plots_dir,
        ),
        methodology=run_config.methodology,
        sampling=run_config.sampling,
        runtime=run_config.runtime,
    )


def infer_capture_details(path: Path) -> tuple[CaptureFormat | None, CompressionType]:
    """Infer capture format and compression wrapper from a capture path."""

    suffixes = [suffix.lower() for suffix in path.suffixes]
    if not suffixes:
        raise ValueError(f"Unsupported raw file without a capture or archive suffix: {path}")

    if suffixes[-1] == ".pcap":
        return CaptureFormat.PCAP, CompressionType.NONE
    if suffixes[-1] == ".pcapng":
        return CaptureFormat.PCAPNG, CompressionType.NONE
    if suffixes[-1] == ".gz":
        return _capture_from_base_suffixes(path, suffixes[:-1]), CompressionType.GZIP
    if suffixes[-1] == ".xz":
        return _capture_from_base_suffixes(path, suffixes[:-1]), CompressionType.XZ
    if suffixes[-1] == ".zip":
        return None, CompressionType.ZIP
    if suffixes[-1] == ".rar":
        return None, CompressionType.RAR

    raise ValueError(f"Unsupported raw file type for dataset registry: {path}")


def _capture_from_base_suffixes(path: Path, base_suffixes: list[str]) -> CaptureFormat:
    if not base_suffixes:
        raise ValueError(f"Compressed file is missing a capture suffix before the wrapper: {path}")
    if base_suffixes[-1] == ".pcap":
        return CaptureFormat.PCAP
    if base_suffixes[-1] == ".pcapng":
        return CaptureFormat.PCAPNG
    raise ValueError(f"Compressed file does not resolve to a supported capture format: {path}")


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


def _get_section(raw_data: dict[str, Any], section: str, *, required: bool = True) -> dict[str, Any]:
    value = raw_data.get(section, {})
    if value is None and not required:
        return {}
    if not isinstance(value, dict):
        raise ConfigError(f"{section} must be a mapping.")
    if required and not value:
        raise ConfigError(f"{section} is required.")
    return value


def _resolve_path(value: str, base_dir: Path) -> Path:
    candidate = Path(value).expanduser()
    if not candidate.is_absolute():
        candidate = (base_dir / candidate).resolve()
    return candidate


def _parse_flow_key(value: Any) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        raise ConfigError("methodology.flow_key_fields must be a list of field names.")
    fields = tuple(_require_non_empty_string(item, "methodology.flow_key_fields[]") for item in value)
    if len(fields) != len(set(fields)):
        raise ConfigError("methodology.flow_key_fields must not contain duplicates.")
    return fields


def _parse_size_basis(value: Any) -> SizeBasis:
    try:
        return SizeBasis(str(value))
    except ValueError as exc:
        raise ConfigError("methodology.size_basis must be one of packets, bytes, or both.") from exc


def _parse_sampling_method(value: Any) -> SamplingMethod:
    try:
        return SamplingMethod(str(value))
    except ValueError as exc:
        raise ConfigError("sampling.method must be one of systematic or random.") from exc


def _parse_byte_basis(value: Any) -> ByteBasis:
    try:
        return ByteBasis(str(value))
    except ValueError as exc:
        raise ConfigError("methodology.byte_basis must be one of: captured_len.") from exc


def _parse_sampling_rates(value: Any) -> tuple[int, ...]:
    if not isinstance(value, (list, tuple)):
        raise ConfigError("sampling.rates must be a list of integers expressed as X in 1:X.")
    rates = tuple(_require_positive_int(item, "sampling.rates[]") for item in value)
    if not rates:
        raise ConfigError("sampling.rates must include at least one rate.")
    return rates


def _parse_cache_policy(value: Any) -> CachePolicy:
    try:
        return CachePolicy(str(value))
    except ValueError as exc:
        raise V2ConfigError("runtime.cache_policy must be one of: none, minimal, debug.") from exc


def _parse_plotting_mode(value: Any) -> str:
    if isinstance(value, bool):
        return DEFAULT_PLOTTING_MODE if value else "off"
    return _require_non_empty_string(value, "runtime.plotting_mode")


def _require_non_empty_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"{field_name} must be a non-empty string.")
    return value.strip()


def _optional_string(value: Any, field_name: str, *, default: str) -> str:
    if value is None:
        return default
    return _require_non_empty_string(value, field_name)


def _require_positive_int(value: Any, field_name: str) -> int:
    if not isinstance(value, int) or value <= 0:
        raise ConfigError(f"{field_name} must be a positive integer.")
    return value


def _optional_int(value: Any, field_name: str) -> int | None:
    if value is None:
        return None
    if not isinstance(value, int):
        raise ConfigError(f"{field_name} must be an integer when provided.")
    return value
