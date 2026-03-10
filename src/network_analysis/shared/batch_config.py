"""YAML-backed configuration loading for dataset-folder batch runs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .config import (
    ConfigError,
    MethodologyConfig,
    RuntimeConfig,
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

DEFAULT_DATASET_GLOB = "*"


class BatchConfigError(ConfigError):
    """Raised when batch configuration content is invalid."""


@dataclass(frozen=True)
class BatchDiscoveryConfig:
    """Dataset-root scanning settings."""

    datasets_root: Path
    dataset_glob: str = DEFAULT_DATASET_GLOB


@dataclass(frozen=True)
class BatchOutputConfig:
    """Root output locations for batch execution."""

    staged_root: Path
    processed_root: Path
    results_root: Path


@dataclass(frozen=True)
class BatchConfig:
    """Top-level batch-runner configuration."""

    config_path: Path
    discovery: BatchDiscoveryConfig
    output: BatchOutputConfig
    methodology: MethodologyConfig
    sampling: SamplingConfig
    runtime: RuntimeConfig

    def summary_lines(self) -> tuple[str, ...]:
        """Render a concise summary for batch CLI validation output."""

        return (
            f"Batch config: {self.config_path}",
            f"Datasets root: {self.discovery.datasets_root}",
            f"Dataset glob: {self.discovery.dataset_glob}",
            f"Flow key: {', '.join(self.methodology.flow_key_fields)}",
            f"Inactivity timeout: {self.methodology.inactivity_timeout_seconds}s",
            f"Sampling rates: {', '.join(f'1:{rate}' for rate in self.sampling.normalized_rates())}",
            f"Sampling method: {self.sampling.method}",
            f"Size basis: {self.methodology.size_basis}",
            f"Byte basis: {self.methodology.byte_basis}",
            f"Staged root: {self.output.staged_root}",
            f"Processed root: {self.output.processed_root}",
            f"Results root: {self.output.results_root}",
            f"Workers: {self.runtime.workers}",
            f"Plots enabled: {self.runtime.enable_plots}",
        )


def load_batch_config(path: str | Path) -> BatchConfig:
    """Load and validate a batch-runner configuration file."""

    import yaml

    try:
        config_path = Path(path).expanduser().resolve()
        raw_data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        if not isinstance(raw_data, dict):
            raise BatchConfigError("Top-level batch config must be a mapping.")

        base_dir = config_path.parent
        discovery_data = _get_section(raw_data, "discovery")
        output_data = _get_section(raw_data, "output")
        methodology_data = _get_section(raw_data, "methodology", required=False)
        sampling_data = _get_section(raw_data, "sampling", required=False)
        runtime_data = _get_section(raw_data, "runtime", required=False)

        discovery = BatchDiscoveryConfig(
            datasets_root=_resolve_path(
                _require_non_empty_string(discovery_data.get("datasets_root"), "discovery.datasets_root"),
                base_dir,
            ),
            dataset_glob=_optional_string(
                discovery_data.get("dataset_glob"),
                "discovery.dataset_glob",
                default=DEFAULT_DATASET_GLOB,
            ),
        )
        methodology = MethodologyConfig(
            flow_key_fields=_parse_flow_key(
                methodology_data.get("flow_key_fields", MethodologyConfig.flow_key_fields)
            ),
            inactivity_timeout_seconds=_require_positive_int(
                methodology_data.get(
                    "inactivity_timeout_seconds",
                    MethodologyConfig.inactivity_timeout_seconds,
                ),
                "methodology.inactivity_timeout_seconds",
            ),
            size_basis=_parse_size_basis(methodology_data.get("size_basis", MethodologyConfig.size_basis.value)),
            byte_basis=_parse_byte_basis(methodology_data.get("byte_basis", MethodologyConfig.byte_basis.value)),
        )
        sampling = SamplingConfig(
            rates=_parse_sampling_rates(sampling_data.get("rates", SamplingConfig.rates)),
            method=_parse_sampling_method(sampling_data.get("method", SamplingConfig.method.value)),
            random_seed=_optional_int(sampling_data.get("random_seed"), "sampling.random_seed"),
        )
        runtime = RuntimeConfig(
            workers=_require_positive_int(runtime_data.get("workers", 1), "runtime.workers"),
            enable_plots=bool(runtime_data.get("enable_plots", False)),
        )
        output = BatchOutputConfig(
            staged_root=_resolve_path(
                _optional_string(output_data.get("staged_root"), "output.staged_root", default="../data/staged"),
                base_dir,
            ),
            processed_root=_resolve_path(
                _optional_string(
                    output_data.get("processed_root"),
                    "output.processed_root",
                    default="../data/processed",
                ),
                base_dir,
            ),
            results_root=_resolve_path(
                _optional_string(output_data.get("results_root"), "output.results_root", default="../results"),
                base_dir,
            ),
        )

        return BatchConfig(
            config_path=config_path,
            discovery=discovery,
            output=output,
            methodology=methodology,
            sampling=sampling,
            runtime=runtime,
        )
    except BatchConfigError:
        raise
    except ConfigError as exc:
        raise BatchConfigError(str(exc)) from exc
