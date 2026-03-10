"""Base contracts shared by stage modules."""

from dataclasses import dataclass

from network_analysis.shared.config import PipelineConfig
from network_analysis.shared.types import ArtifactContract, StageName


class StageNotImplementedError(NotImplementedError):
    """Raised when a stage placeholder is invoked before implementation."""


@dataclass(frozen=True)
class StageContract:
    """Static description of a pipeline stage module."""

    name: StageName
    description: str
    inputs: tuple[str, ...]
    outputs: tuple[ArtifactContract, ...]
    implemented: bool = False

    def resolve_output_paths(self, config: PipelineConfig) -> tuple[str, ...]:
        """Resolve artifact templates using the configured dataset identifier."""

        dataset_id = config.dataset.dataset_id
        return tuple(
            artifact.relative_path_template.format(dataset_id=dataset_id)
            for artifact in self.outputs
        )

