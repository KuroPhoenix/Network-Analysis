"""Plotting stage contract."""

from network_analysis.shared.config import PipelineConfig
from network_analysis.shared.types import ArtifactContract, ArtifactKind, StageName
from network_analysis.stages.base import StageContract, StageNotImplementedError

STAGE_CONTRACT = StageContract(
    name=StageName.PLOTTING,
    description="Render minimal reproducible plots from computed metric tables.",
    inputs=(
        "metric summary table",
        "flow metric table",
        "plot selection",
    ),
    outputs=(
        ArtifactContract(
            name="plots",
            relative_path_template="results/plots/{dataset_id}/",
            format="png",
            description="Static plots generated from metric tables.",
            kind=ArtifactKind.DIRECTORY,
        ),
    ),
)


def describe_stage() -> StageContract:
    """Return the static stage contract."""

    return STAGE_CONTRACT


def run_stage(config: PipelineConfig) -> None:
    """Placeholder entrypoint for the plotting stage."""

    raise StageNotImplementedError(
        f"{STAGE_CONTRACT.name} is not implemented yet. Use the Stage 1 CLI in dry-run mode."
    )

