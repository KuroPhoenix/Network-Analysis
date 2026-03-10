"""Sampling module contract."""

from .base import ModuleContract, ModuleNotImplementedError
from ..shared.constants import PREFERRED_TABULAR_FORMAT
from ..shared.config import PipelineConfig
from ..shared.types import ArtifactContract, ArtifactKind, ModuleName

MODULE_CONTRACT = ModuleContract(
    name=ModuleName.SAMPLING,
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


def describe_module() -> ModuleContract:
    """Return the static module contract."""

    return MODULE_CONTRACT


def run_module(config: PipelineConfig) -> None:
    """Placeholder entrypoint for the sampling module."""

    raise ModuleNotImplementedError(
        f"{MODULE_CONTRACT.name} is not implemented yet. Use the current CLI in dry-run mode."
    )
