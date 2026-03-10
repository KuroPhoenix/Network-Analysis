"""Ingest and decompression stage contract."""

from network_analysis.shared.constants import PREFERRED_TABULAR_FORMAT
from network_analysis.shared.config import PipelineConfig
from network_analysis.shared.types import ArtifactContract, ArtifactKind, StageName
from network_analysis.stages.base import StageContract, StageNotImplementedError

STAGE_CONTRACT = StageContract(
    name=StageName.INGEST,
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
)


def describe_stage() -> StageContract:
    """Return the static stage contract."""

    return STAGE_CONTRACT


def run_stage(config: PipelineConfig) -> None:
    """Placeholder entrypoint for the ingest stage."""

    raise StageNotImplementedError(
        f"{STAGE_CONTRACT.name} is not implemented yet. Use the Stage 1 CLI in dry-run mode."
    )

