"""Internal bridge configuration objects for the executable module pipeline."""

from dataclasses import dataclass
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
from .types import ByteBasis, SamplingMethod, SizeBasis


class ConfigError(ValueError):
    """Raised when configuration content is invalid."""


@dataclass(frozen=True)
class DatasetConfig:
    """Dataset discovery settings."""

    dataset_id: str
    input_dir: Path
    raw_glob: str = "*"


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
class RuntimeConfig:
    """Runtime and orchestration options for local execution."""

    workers: int = 1
    enable_plots: bool = False


@dataclass(frozen=True)
class PipelineConfig:
    """Top-level pipeline configuration."""

    config_path: Path
    dataset: DatasetConfig
    output: OutputConfig
    methodology: MethodologyConfig
    sampling: SamplingConfig
    runtime: RuntimeConfig

    def summary_lines(self) -> tuple[str, ...]:
        """Render a concise summary for CLI validation output."""

        return (
            f"Config: {self.config_path}",
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
            f"Plots enabled: {self.runtime.enable_plots}",
        )


def load_pipeline_config(path: str | Path) -> PipelineConfig:
    """Load and validate an internal bridge pipeline configuration file."""

    config_path = Path(path).expanduser().resolve()
    raw_data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw_data, dict):
        raise ConfigError("Top-level config must be a mapping.")

    base_dir = config_path.parent
    dataset_data = _get_section(raw_data, "dataset")
    output_data = _get_section(raw_data, "output")
    methodology_data = _get_section(raw_data, "methodology", required=False)
    sampling_data = _get_section(raw_data, "sampling", required=False)
    runtime_data = _get_section(raw_data, "runtime", required=False)

    dataset = DatasetConfig(
        dataset_id=_require_non_empty_string(dataset_data.get("dataset_id"), "dataset.dataset_id"),
        input_dir=_resolve_path(
            _require_non_empty_string(dataset_data.get("input_dir"), "dataset.input_dir"),
            base_dir,
        ),
        raw_glob=_optional_string(dataset_data.get("raw_glob"), "dataset.raw_glob", default="*"),
    )
    methodology = MethodologyConfig(
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
    )
    sampling = SamplingConfig(
        rates=_parse_sampling_rates(sampling_data.get("rates", DEFAULT_SAMPLING_RATES)),
        method=_parse_sampling_method(sampling_data.get("method", DEFAULT_SAMPLING_METHOD)),
        random_seed=_optional_int(sampling_data.get("random_seed"), "sampling.random_seed"),
    )
    runtime = RuntimeConfig(
        workers=_require_positive_int(runtime_data.get("workers", 1), "runtime.workers"),
        enable_plots=bool(runtime_data.get("enable_plots", False)),
    )
    output = OutputConfig(
        staged_dir=_resolve_path(
            _optional_string(output_data.get("staged_dir"), "output.staged_dir", default="../data/staged"),
            base_dir,
        ),
        processed_dir=_resolve_path(
            _optional_string(output_data.get("processed_dir"), "output.processed_dir", default="../data/processed"),
            base_dir,
        ),
        results_tables_dir=_resolve_path(
            _optional_string(
                output_data.get("results_tables_dir"),
                "output.results_tables_dir",
                default="../results/tables",
            ),
            base_dir,
        ),
        results_plots_dir=_resolve_path(
            _optional_string(
                output_data.get("results_plots_dir"),
                "output.results_plots_dir",
                default="../results/plots",
            ),
            base_dir,
        ),
    )

    return PipelineConfig(
        config_path=config_path,
        dataset=dataset,
        output=output,
        methodology=methodology,
        sampling=sampling,
        runtime=runtime,
    )


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
