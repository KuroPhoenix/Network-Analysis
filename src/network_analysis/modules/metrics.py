"""Metric computation module contract."""

from .base import ModuleContract, ModuleNotImplementedError
from ..shared.constants import PREFERRED_TABULAR_FORMAT
from ..shared.config import PipelineConfig
from ..shared.types import ArtifactContract, ModuleName

MODULE_CONTRACT = ModuleContract(
    name=ModuleName.METRICS,
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


def describe_module() -> ModuleContract:
    """Return the static module contract."""

    return MODULE_CONTRACT


def run_module(config: PipelineConfig) -> None:
    """Placeholder entrypoint for the metric module."""

    raise ModuleNotImplementedError(
        f"{MODULE_CONTRACT.name} is not implemented yet. Use the current CLI in dry-run mode."
    )
