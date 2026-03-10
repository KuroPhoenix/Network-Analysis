"""Sampling stage contract."""

from network_analysis.shared.constants import PREFERRED_TABULAR_FORMAT
from network_analysis.shared.config import PipelineConfig
from network_analysis.shared.types import ArtifactContract, ArtifactKind, StageName
from network_analysis.stages.base import StageContract, StageNotImplementedError

STAGE_CONTRACT = StageContract(
    name=StageName.SAMPLING,
    description="Generate sampled packet or flow artefacts for configured 1:X rates.",
    inputs=(
        "canonical packet table",
        "baseline flows",
        "sampling rates",
        "sampling method",
        "random seed when applicable",
    ),
    outputs=(
        ArtifactContract(
            name="sampled_flows",
            relative_path_template="data/processed/{dataset_id}/sampled_flows/",
            format=PREFERRED_TABULAR_FORMAT,
            description="Directory for per-rate sampled flow tables.",
            kind=ArtifactKind.DIRECTORY,
        ),
        ArtifactContract(
            name="sampling_run_manifest",
            relative_path_template="data/processed/{dataset_id}/sampling_runs.parquet",
            format=PREFERRED_TABULAR_FORMAT,
            description="Structured metadata for each sampling run.",
        ),
    ),
)


def describe_stage() -> StageContract:
    """Return the static stage contract."""

    return STAGE_CONTRACT


def run_stage(config: PipelineConfig) -> None:
    """Placeholder entrypoint for the sampling stage."""

    raise StageNotImplementedError(
        f"{STAGE_CONTRACT.name} is not implemented yet. Use the Stage 1 CLI in dry-run mode."
    )

