"""Dataset registry and validation module implementation."""

from __future__ import annotations

import gzip
import lzma
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

PCAP_MAGIC_HEADERS = {
    b"\xd4\xc3\xb2\xa1",
    b"\xa1\xb2\xc3\xd4",
    b"\x4d\x3c\xb2\xa1",
    b"\xa1\xb2\x3c\x4d",
}
PCAPNG_MAGIC_HEADER = b"\x0a\x0d\x0d\x0a"
CAPTURE_HEADER_BYTES = 4


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

    return [(path, *infer_capture_details(path)) for path in raw_files]


def infer_capture_details(path: Path) -> tuple[CaptureFormat | None, CompressionType]:
    suffixes = [suffix.lower() for suffix in path.suffixes]
    if not suffixes:
        raise ValueError(f"Unsupported raw file without a capture or archive suffix: {path}")

    if suffixes[-1] == ".pcap":
        return _detect_capture_format_for_wrapper(path, CompressionType.NONE), CompressionType.NONE
    if suffixes[-1] == ".pcapng":
        return _detect_capture_format_for_wrapper(path, CompressionType.NONE), CompressionType.NONE
    if suffixes[-1] == ".gz":
        return _detect_capture_format_for_wrapper(path, CompressionType.GZIP), CompressionType.GZIP
    if suffixes[-1] == ".xz":
        return _detect_capture_format_for_wrapper(path, CompressionType.XZ), CompressionType.XZ
    if suffixes[-1] == ".zip":
        return None, CompressionType.ZIP
    if suffixes[-1] == ".rar":
        return None, CompressionType.RAR

    raise ValueError(f"Unsupported raw file type for dataset registry: {path}")


def detect_capture_format(path: Path, compression_type: CompressionType = CompressionType.NONE) -> CaptureFormat:
    """Detect the capture format from readable bytes instead of only trusting suffixes."""

    header = _read_capture_header(path, compression_type)
    try:
        return detect_capture_format_from_header_bytes(header)
    except ValueError as exc:
        raise ValueError(f"Could not detect a supported capture format from file header: {path}") from exc


def detect_capture_format_from_header_bytes(header: bytes) -> CaptureFormat:
    """Detect a supported capture format from already-readable header bytes."""

    capture_format = _capture_format_from_header(header)
    if capture_format is None:
        raise ValueError("Could not detect a supported capture format from readable bytes.")
    return capture_format


def _detect_capture_format_for_wrapper(path: Path, compression_type: CompressionType) -> CaptureFormat:
    return detect_capture_format(path, compression_type)


def _read_capture_header(path: Path, compression_type: CompressionType) -> bytes:
    if compression_type == CompressionType.NONE:
        with path.open("rb") as handle:
            return handle.read(CAPTURE_HEADER_BYTES)
    if compression_type == CompressionType.GZIP:
        with gzip.open(path, "rb") as handle:
            return handle.read(CAPTURE_HEADER_BYTES)
    if compression_type == CompressionType.XZ:
        with lzma.open(path, "rb") as handle:
            return handle.read(CAPTURE_HEADER_BYTES)
    raise ValueError(f"Capture-header detection is not available for wrapper {compression_type}: {path}")


def _capture_format_from_header(header: bytes) -> CaptureFormat | None:
    if len(header) < CAPTURE_HEADER_BYTES:
        return None
    if header[:CAPTURE_HEADER_BYTES] in PCAP_MAGIC_HEADERS:
        return CaptureFormat.PCAP
    if header[:CAPTURE_HEADER_BYTES] == PCAPNG_MAGIC_HEADER:
        return CaptureFormat.PCAPNG
    return None
