"""Metric computation stage contract."""

from network_analysis.shared.constants import PREFERRED_TABULAR_FORMAT
from network_analysis.shared.config import PipelineConfig
from network_analysis.shared.types import ArtifactContract, StageName
from network_analysis.stages.base import StageContract, StageNotImplementedError

STAGE_CONTRACT = StageContract(
    name=StageName.METRICS,
    description="Compare each 1:X sampled run directly against the 1:1 baseline.",
    inputs=(
        "baseline flows",
        "sampled flows",
        "size basis",
        "flow-key definition",
        "inactivity timeout",
    ),
    outputs=(
        ArtifactContract(
            name="metric_summary",
            relative_path_template="results/tables/{dataset_id}_metric_summary.parquet",
            format=PREFERRED_TABULAR_FORMAT,
            description="Per-rate summary metrics including detection rate.",
        ),
        ArtifactContract(
            name="flow_metrics",
            relative_path_template="results/tables/{dataset_id}_flow_metrics.parquet",
            format=PREFERRED_TABULAR_FORMAT,
            description="Per-flow distortion metrics matched against the baseline.",
        ),
    ),
)


def describe_stage() -> StageContract:
    """Return the static stage contract."""

    return STAGE_CONTRACT


def run_stage(config: PipelineConfig) -> None:
    """Placeholder entrypoint for the metric stage."""

    raise StageNotImplementedError(
        f"{STAGE_CONTRACT.name} is not implemented yet. Use the Stage 1 CLI in dry-run mode."
    )

