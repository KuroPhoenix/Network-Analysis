"""Packet extraction stage contract."""

from network_analysis.shared.constants import PREFERRED_TABULAR_FORMAT
from network_analysis.shared.config import PipelineConfig
from network_analysis.shared.types import ArtifactContract, StageName
from network_analysis.stages.base import StageContract, StageNotImplementedError

STAGE_CONTRACT = StageContract(
    name=StageName.PACKET_EXTRACTION,
    description="Extract canonical packet metadata tables from staged packet captures.",
    inputs=(
        "ingest manifest",
        "staged capture files",
        "packet parser configuration",
    ),
    outputs=(
        ArtifactContract(
            name="canonical_packet_table",
            relative_path_template="data/processed/{dataset_id}/packets.parquet",
            format=PREFERRED_TABULAR_FORMAT,
            description="Canonical packet table used by downstream flow reconstruction.",
        ),
    ),
)


def describe_stage() -> StageContract:
    """Return the static stage contract."""

    return STAGE_CONTRACT


def run_stage(config: PipelineConfig) -> None:
    """Placeholder entrypoint for the packet extraction stage."""

    raise StageNotImplementedError(
        f"{STAGE_CONTRACT.name} is not implemented yet. Use the Stage 1 CLI in dry-run mode."
    )

