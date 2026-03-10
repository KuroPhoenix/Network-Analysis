"""Dataset registry and validation module implementation."""

from pathlib import Path

from .base import ModuleContract
from ..shared.artifacts import build_artifact_paths
from ..shared.constants import PREFERRED_TABULAR_FORMAT
from ..shared.config import PipelineConfig
from ..shared.types import ArtifactContract, CaptureFormat, CompressionType, ModuleName

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


def run_module(config: PipelineConfig) -> Path:
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
    config: PipelineConfig,
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

    return [(path, *_infer_capture_details(path)) for path in raw_files]


def _infer_capture_details(path: Path) -> tuple[CaptureFormat | None, CompressionType]:
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
