"""Ingest and decompression module implementation."""

import gzip
from hashlib import sha256
import lzma
from pathlib import Path
import shutil
import zipfile

from .base import ModuleContract
from ..shared.artifacts import build_artifact_paths
from ..shared.constants import PREFERRED_TABULAR_FORMAT
from ..shared.config import PipelineConfig
from ..shared.types import (
    ArtifactContract,
    ArtifactKind,
    CaptureFormat,
    CompressionType,
    ModuleName,
)

MODULE_CONTRACT = ModuleContract(
    name=ModuleName.INGEST,
    description="Discover raw captures, preserve them immutably, and stage readable packet captures.",
    inputs=(
        "dataset registry manifest",
        "raw capture files",
        "supported compression settings",
    ),
    outputs=(
        ArtifactContract(
            name="staged_captures",
            relative_path_template="data/staged/{dataset_id}/",
            format="pcap/pcapng",
            description="Immutable staged capture files ready for parsing.",
            kind=ArtifactKind.DIRECTORY,
        ),
        ArtifactContract(
            name="ingest_manifest",
            relative_path_template="data/processed/{dataset_id}/ingest_manifest.parquet",
            format=PREFERRED_TABULAR_FORMAT,
            description="Structured metadata describing staged capture files.",
        ),
    ),
    implemented=True,
)


def describe_module() -> ModuleContract:
    """Return the static module contract."""

    return MODULE_CONTRACT


def run_module(config: PipelineConfig) -> Path:
    """Stage immutable packet-capture files for parsing."""

    import polars as pl

    artifact_paths = build_artifact_paths(config)
    if not artifact_paths.dataset_registry.exists():
        raise FileNotFoundError(
            f"Dataset registry manifest is missing. Run {ModuleName.DATASET_REGISTRY} first: "
            f"{artifact_paths.dataset_registry}"
        )

    registry_frame = pl.read_parquet(artifact_paths.dataset_registry)
    if registry_frame.is_empty():
        raise ValueError("Dataset registry manifest is empty.")

    artifact_paths.staged_dir.mkdir(parents=True, exist_ok=True)
    artifact_paths.processed_dir.mkdir(parents=True, exist_ok=True)

    manifest_rows: list[dict[str, object]] = []
    for row in registry_frame.iter_rows(named=True):
        manifest_rows.extend(_stage_registry_row(row, artifact_paths.staged_dir))

    if not manifest_rows:
        raise ValueError("Ingest did not stage any capture files.")

    pl.DataFrame(manifest_rows).write_parquet(artifact_paths.ingest_manifest)
    return artifact_paths.ingest_manifest


def _stage_registry_row(row: dict[str, object], staged_dir: Path) -> list[dict[str, object]]:
    source_file = Path(str(row["raw_file"]))
    compression_type = CompressionType(str(row["compression_type"]))

    if compression_type == CompressionType.NONE:
        capture_format = CaptureFormat(str(row["capture_format_hint"]))
        staged_file = staged_dir / source_file.name
        shutil.copy2(source_file, staged_file)
        return [
            _build_manifest_row(
                dataset_id=str(row["dataset_id"]),
                source_file=source_file,
                staged_file=staged_file,
                staging_action="copied",
                capture_format=capture_format,
                compression_type=compression_type,
            )
        ]

    if compression_type == CompressionType.GZIP:
        staged_file = staged_dir / source_file.name.removesuffix(".gz")
        with gzip.open(source_file, "rb") as source_handle, staged_file.open("wb") as target_handle:
            shutil.copyfileobj(source_handle, target_handle)
        capture_format = _infer_staged_capture_format(staged_file)
        return [
            _build_manifest_row(
                dataset_id=str(row["dataset_id"]),
                source_file=source_file,
                staged_file=staged_file,
                staging_action="decompressed_gzip",
                capture_format=capture_format,
                compression_type=compression_type,
            )
        ]

    if compression_type == CompressionType.XZ:
        staged_file = staged_dir / source_file.name.removesuffix(".xz")
        with lzma.open(source_file, "rb") as source_handle, staged_file.open("wb") as target_handle:
            shutil.copyfileobj(source_handle, target_handle)
        capture_format = _infer_staged_capture_format(staged_file)
        return [
            _build_manifest_row(
                dataset_id=str(row["dataset_id"]),
                source_file=source_file,
                staged_file=staged_file,
                staging_action="decompressed_xz",
                capture_format=capture_format,
                compression_type=compression_type,
            )
        ]

    if compression_type == CompressionType.ZIP:
        manifest_rows: list[dict[str, object]] = []
        with zipfile.ZipFile(source_file) as archive:
            capture_members = [
                member
                for member in archive.infolist()
                if not member.is_dir()
                and Path(member.filename).suffix.lower() in {".pcap", ".pcapng"}
            ]
            if not capture_members:
                raise ValueError(f"No .pcap or .pcapng member found in ZIP archive: {source_file}")

            for member in capture_members:
                member_name = Path(member.filename).name
                staged_file = staged_dir / f"{source_file.stem}__{member_name}"
                with archive.open(member, "r") as source_handle, staged_file.open("wb") as target_handle:
                    shutil.copyfileobj(source_handle, target_handle)
                capture_format = _infer_staged_capture_format(staged_file)
                manifest_rows.append(
                    _build_manifest_row(
                        dataset_id=str(row["dataset_id"]),
                        source_file=source_file,
                        staged_file=staged_file,
                        staging_action=f"extracted_zip:{member.filename}",
                        capture_format=capture_format,
                        compression_type=compression_type,
                    )
                )
        return manifest_rows

    if compression_type == CompressionType.RAR:
        raise ValueError(
            f"RAR archives are not supported by the local MVP ingest stage without extra tooling: {source_file}"
        )

    raise ValueError(f"Unsupported compression type during ingest: {source_file}")


def _build_manifest_row(
    *,
    dataset_id: str,
    source_file: Path,
    staged_file: Path,
    staging_action: str,
    capture_format: CaptureFormat,
    compression_type: CompressionType,
) -> dict[str, object]:
    return {
        "dataset_id": dataset_id,
        "source_file": str(source_file),
        "staged_file": str(staged_file),
        "staging_action": staging_action,
        "capture_format": capture_format.value,
        "compression_type": compression_type.value,
        "source_sha256": _sha256_file(source_file),
        "staged_sha256": _sha256_file(staged_file),
        "source_size_bytes": source_file.stat().st_size,
        "staged_size_bytes": staged_file.stat().st_size,
    }


def _infer_staged_capture_format(path: Path) -> CaptureFormat:
    suffix = path.suffix.lower()
    if suffix == ".pcap":
        return CaptureFormat.PCAP
    if suffix == ".pcapng":
        return CaptureFormat.PCAPNG
    raise ValueError(f"Unsupported staged capture format: {path}")


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
