"""Ground-truth flow construction stage contract."""

from network_analysis.shared.constants import PREFERRED_TABULAR_FORMAT
from network_analysis.shared.config import PipelineConfig
from network_analysis.shared.types import ArtifactContract, StageName
from network_analysis.stages.base import StageContract, StageNotImplementedError

STAGE_CONTRACT = StageContract(
    name=StageName.FLOW_CONSTRUCTION,
    description="Reconstruct unsampled directional baseline flows from canonical packets.",
    inputs=(
        "canonical packet table",
        "flow-key definition",
        "inactivity timeout",
        "size basis",
    ),
    outputs=(
        ArtifactContract(
            name="baseline_flows",
            relative_path_template="data/processed/{dataset_id}/baseline_flows.parquet",
            format=PREFERRED_TABULAR_FORMAT,
            description="Ground-truth 1:1 baseline flow records.",
        ),
    ),
)


def describe_stage() -> StageContract:
    """Return the static stage contract."""

    return STAGE_CONTRACT


def run_stage(config: PipelineConfig) -> None:
    """Placeholder entrypoint for the flow construction stage."""

    raise StageNotImplementedError(
        f"{STAGE_CONTRACT.name} is not implemented yet. Use the Stage 1 CLI in dry-run mode."
    )

