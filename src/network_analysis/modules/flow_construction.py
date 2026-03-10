"""Ground-truth flow construction module contract."""

from .base import ModuleContract, ModuleNotImplementedError
from ..shared.constants import PREFERRED_TABULAR_FORMAT
from ..shared.config import PipelineConfig
from ..shared.types import ArtifactContract, ModuleName

MODULE_CONTRACT = ModuleContract(
    name=ModuleName.FLOW_CONSTRUCTION,
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


def describe_module() -> ModuleContract:
    """Return the static module contract."""

    return MODULE_CONTRACT


def run_module(config: PipelineConfig) -> None:
    """Placeholder entrypoint for the flow construction module."""

    raise ModuleNotImplementedError(
        f"{MODULE_CONTRACT.name} is not implemented yet. Use the current CLI in dry-run mode."
    )
