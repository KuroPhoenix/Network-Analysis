"""Plotting module contract."""

from .base import ModuleContract, ModuleNotImplementedError
from ..shared.config import PipelineConfig
from ..shared.types import ArtifactContract, ArtifactKind, ModuleName

MODULE_CONTRACT = ModuleContract(
    name=ModuleName.PLOTTING,
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


def describe_module() -> ModuleContract:
    """Return the static module contract."""

    return MODULE_CONTRACT


def run_module(config: PipelineConfig) -> None:
    """Placeholder entrypoint for the plotting module."""

    raise ModuleNotImplementedError(
        f"{MODULE_CONTRACT.name} is not implemented yet. Use the current CLI in dry-run mode."
    )
