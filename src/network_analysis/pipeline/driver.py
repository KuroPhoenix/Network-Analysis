"""Thin driver that composes the stage modules."""

from dataclasses import dataclass

from network_analysis.shared.config import PipelineConfig
from network_analysis.stages import (
    dataset_registry,
    flow_construction,
    ingest,
    metrics,
    packet_extraction,
    plotting,
    sampling,
)
from network_analysis.stages.base import StageContract

STAGE_MODULES = (
    dataset_registry,
    ingest,
    packet_extraction,
    flow_construction,
    sampling,
    metrics,
    plotting,
)


@dataclass(frozen=True)
class PlannedStage:
    """A resolved stage entry in the driver plan."""

    contract: StageContract
    resolved_outputs: tuple[str, ...]


def get_stage_catalog() -> tuple[StageContract, ...]:
    """Return the named stage catalog in execution order."""

    return tuple(module.describe_stage() for module in STAGE_MODULES)


def plan_pipeline(config: PipelineConfig) -> tuple[PlannedStage, ...]:
    """Build a dry-run execution plan from the configured stage catalog."""

    return tuple(
        PlannedStage(contract=contract, resolved_outputs=contract.resolve_output_paths(config))
        for contract in get_stage_catalog()
    )


def render_pipeline_plan(config: PipelineConfig) -> str:
    """Render the pipeline plan for CLI output."""

    lines = [
        "Stage 1 pipeline plan",
        f"Dataset: {config.dataset.dataset_id}",
        f"Sampling rates: {', '.join(f'1:{rate}' for rate in config.sampling.normalized_rates())}",
        f"Flow key: {', '.join(config.methodology.flow_key_fields)}",
        f"Inactivity timeout: {config.methodology.inactivity_timeout_seconds}s",
        f"Size basis: {config.methodology.size_basis}",
        "",
    ]
    for stage in plan_pipeline(config):
        lines.append(f"{stage.contract.name}: {stage.contract.description}")
        for output in stage.resolved_outputs:
            lines.append(f"  output -> {output}")
    return "\n".join(lines)


def run_pipeline(config: PipelineConfig, *, dry_run: bool = False) -> tuple[PlannedStage, ...]:
    """Run or dry-run the pipeline using the stage modules."""

    planned_stages = plan_pipeline(config)
    if dry_run:
        return planned_stages

    for module in STAGE_MODULES:
        module.run_stage(config)

    return planned_stages

