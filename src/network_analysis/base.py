"""Base contracts shared by pipeline modules."""

from dataclasses import dataclass

from .config import DatasetRunConfig
from .types import ArtifactContract, ModuleName


class ModuleNotImplementedError(NotImplementedError):
    """Raised when a module placeholder is invoked before implementation."""


@dataclass(frozen=True)
class ModuleContract:
    """Static description of a pipeline module."""

    name: ModuleName
    description: str
    inputs: tuple[str, ...]
    outputs: tuple[ArtifactContract, ...]
    implemented: bool = False

    def resolve_output_paths(self, config: DatasetRunConfig) -> tuple[str, ...]:
        """Resolve artifact templates using the configured dataset identifier."""

        dataset_id = config.dataset.dataset_id
        return tuple(
            artifact.relative_path_template.format(dataset_id=dataset_id)
            for artifact in self.outputs
        )
