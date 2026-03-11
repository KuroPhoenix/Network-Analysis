"""Shared types used across pipeline modules."""

from dataclasses import dataclass
from enum import StrEnum


class SizeBasis(StrEnum):
    """Explicit size bases supported by the pipeline."""

    PACKETS = "packets"
    BYTES = "bytes"
    BOTH = "both"


class SamplingMethod(StrEnum):
    """Sampling methods available to later modules."""

    SYSTEMATIC = "systematic"
    RANDOM = "random"


class ByteBasis(StrEnum):
    """Supported byte definitions for flow-size accounting."""

    CAPTURED_LEN = "captured_len"


class CachePolicy(StrEnum):
    """Cache retention policies for the active architecture."""

    NONE = "none"
    MINIMAL = "minimal"
    DEBUG = "debug"


class CaptureFormat(StrEnum):
    """Packet capture formats supported by the MVP."""

    PCAP = "pcap"
    PCAPNG = "pcapng"


class CompressionType(StrEnum):
    """Compression wrappers supported by the MVP ingest module."""

    NONE = "none"
    GZIP = "gzip"
    XZ = "xz"
    ZIP = "zip"
    RAR = "rar"


class ArtifactKind(StrEnum):
    """High-level artifact types emitted by pipeline modules."""

    DIRECTORY = "directory"
    TABLE = "table"
    CAPTURE = "capture"
    PLOT = "plot"


class ModuleName(StrEnum):
    """Named pipeline modules used in code and documentation."""

    DATASET_REGISTRY = "dataset_registry"
    INGEST = "ingest"
    PACKET_EXTRACTION = "packet_extraction"
    FLOW_CONSTRUCTION = "flow_construction"
    SAMPLING = "sampling"
    METRICS = "metrics"
    PLOTTING = "plotting"


@dataclass(frozen=True)
class TableColumn:
    """Column-level schema metadata for documented tabular outputs."""

    name: str
    dtype: str
    description: str
    required: bool = True


@dataclass(frozen=True)
class TableSchema:
    """A documented schema for an expected Parquet or tabular artifact."""

    name: str
    format: str
    columns: tuple[TableColumn, ...]


@dataclass(frozen=True)
class ArtifactContract:
    """An artifact emitted by a pipeline module."""

    name: str
    relative_path_template: str
    format: str
    description: str
    kind: ArtifactKind = ArtifactKind.TABLE
