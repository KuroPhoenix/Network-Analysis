"""Dataset registry and validation stage contract."""

from network_analysis.shared.constants import PREFERRED_TABULAR_FORMAT
from network_analysis.shared.config import PipelineConfig
from network_analysis.shared.types import ArtifactContract, ArtifactKind, StageName
from network_analysis.stages.base import StageContract, StageNotImplementedError

STAGE_CONTRACT = StageContract(
    name=StageName.DATASET_REGISTRY,
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
)


def describe_stage() -> StageContract:
    """Return the static stage contract."""

    return STAGE_CONTRACT


def run_stage(config: PipelineConfig) -> None:
    """Placeholder entrypoint for the dataset registry stage."""

    raise StageNotImplementedError(
        f"{STAGE_CONTRACT.name} is not implemented yet. Use the Stage 1 CLI in dry-run mode."
    )

