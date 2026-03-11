"""Dataset registry and validation module implementation."""

from pathlib import Path

from .artifacts import build_artifact_paths
from .base import ModuleContract
from .config import DatasetRunConfig, infer_capture_details
from .constants import PREFERRED_TABULAR_FORMAT
from .types import ArtifactContract, CaptureFormat, CompressionType, ModuleName

MODULE_CONTRACT = ModuleContract(
    name=ModuleName.DATASET_REGISTRY,
    description="Validate dataset identity, provenance, and raw input location before ingest.",
    inputs=(
        "dataset_id",
        "raw input directory",
        "flow-key definition",
        "inactivity timeout",
    ),
    outputs=(
        ArtifactContract(
            name="dataset_registry",
            relative_path_template="data/processed/{dataset_id}/dataset_registry.parquet",
            format=PREFERRED_TABULAR_FORMAT,
            description="Dataset metadata and immutable provenance manifest.",
        ),
    ),
    implemented=True,
)


def describe_module() -> ModuleContract:
    """Return the static module contract."""

    return MODULE_CONTRACT


def run_module(config: DatasetRunConfig) -> Path:
    """Discover raw files and write the dataset registry manifest."""

    import polars as pl

    artifact_paths = build_artifact_paths(config)
    artifact_paths.processed_dir.mkdir(parents=True, exist_ok=True)

    raw_files = discover_raw_files(config)
    registry_rows = [
        {
            "dataset_id": config.dataset.dataset_id,
            "discovery_index": index,
            "input_dir": str(config.dataset.input_dir),
            "raw_glob": config.dataset.raw_glob,
            "raw_file": str(raw_file),
            "raw_file_size_bytes": raw_file.stat().st_size,
            "capture_format_hint": capture_format.value if capture_format else None,
            "compression_type": compression_type.value,
            "flow_key": ",".join(config.methodology.flow_key_fields),
            "inactivity_timeout_seconds": config.methodology.inactivity_timeout_seconds,
            "size_basis": config.methodology.size_basis.value,
            "byte_basis": config.methodology.byte_basis.value,
        }
        for index, (raw_file, capture_format, compression_type) in enumerate(raw_files, start=1)
    ]

    pl.DataFrame(registry_rows).write_parquet(artifact_paths.dataset_registry)
    return artifact_paths.dataset_registry


def discover_raw_files(
    config: DatasetRunConfig,
) -> list[tuple[Path, CaptureFormat | None, CompressionType]]:
    """Discover and validate raw capture files for the configured dataset."""

    input_dir = config.dataset.input_dir
    if not input_dir.exists():
        raise FileNotFoundError(f"Configured input directory does not exist: {input_dir}")
    if not input_dir.is_dir():
        raise NotADirectoryError(f"Configured input path is not a directory: {input_dir}")

    raw_files = sorted(path for path in input_dir.glob(config.dataset.raw_glob) if path.is_file())
    if not raw_files:
        raise FileNotFoundError(
            f"No raw files matched {config.dataset.raw_glob!r} under {config.dataset.input_dir}"
        )

    return [(path, *infer_capture_details(path)) for path in raw_files]
