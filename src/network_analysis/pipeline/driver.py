"""Thin driver that composes the pipeline modules."""

from dataclasses import dataclass
from time import perf_counter

from ..modules import (
    dataset_registry,
    flow_construction,
    ingest,
    metrics,
    packet_extraction,
    plotting,
    sampling,
)
from ..modules.base import ModuleContract
from ..shared.config import PipelineConfig
from ..shared.runtime_feedback import emit_runtime_event, format_elapsed, progress_bar

PIPELINE_MODULES = (
    dataset_registry,
    ingest,
    packet_extraction,
    flow_construction,
    sampling,
    metrics,
    plotting,
)


@dataclass(frozen=True)
class PlannedModule:
    """A resolved module entry in the driver plan."""

    contract: ModuleContract
    resolved_outputs: tuple[str, ...]


def get_module_catalog() -> tuple[ModuleContract, ...]:
    """Return the named module catalog in execution order."""

    return tuple(module.describe_module() for module in PIPELINE_MODULES)


def plan_pipeline(config: PipelineConfig) -> tuple[PlannedModule, ...]:
    """Build a dry-run execution plan from the configured module catalog."""

    return tuple(
        PlannedModule(contract=contract, resolved_outputs=contract.resolve_output_paths(config))
        for contract in _module_catalog_for_run(config)
    )


def render_pipeline_plan(config: PipelineConfig) -> str:
    """Render the pipeline plan for CLI output."""

    lines = [
        "Pipeline module plan",
        f"Dataset: {config.dataset.dataset_id}",
        f"Sampling rates: {', '.join(f'1:{rate}' for rate in config.sampling.normalized_rates())}",
        f"Flow key: {', '.join(config.methodology.flow_key_fields)}",
        f"Inactivity timeout: {config.methodology.inactivity_timeout_seconds}s",
        f"Size basis: {config.methodology.size_basis}",
        f"Byte basis: {config.methodology.byte_basis}",
        f"Plots enabled: {config.runtime.enable_plots}",
        "",
    ]
    for module in plan_pipeline(config):
        lines.append(f"{module.contract.name}: {module.contract.description}")
        for output in module.resolved_outputs:
            lines.append(f"  output -> {output}")
    return "\n".join(lines)


def run_pipeline(config: PipelineConfig, *, dry_run: bool = False) -> tuple[PlannedModule, ...]:
    """Run or dry-run the pipeline using the pipeline modules."""

    planned_modules = plan_pipeline(config)
    if dry_run:
        return planned_modules

    module_sequence = _module_sequence_for_run(config)
    dataset_id = config.dataset.dataset_id
    pipeline_start = perf_counter()
    emit_runtime_event(
        f"[dataset {dataset_id}] starting pipeline with {len(module_sequence)} modules"
    )

    with progress_bar(
        total=len(module_sequence),
        desc=f"{dataset_id}: modules",
        unit="module",
    ) as bar:
        for module_index, module in enumerate(module_sequence, start=1):
            contract = module.describe_module()
            module_start = perf_counter()
            emit_runtime_event(
                f"[dataset {dataset_id}] [{module_index}/{len(module_sequence)}] {contract.name} starting"
            )
            try:
                module.run_module(config)
            except BaseException:
                module_elapsed = perf_counter() - module_start
                emit_runtime_event(
                    f"[dataset {dataset_id}] [{module_index}/{len(module_sequence)}] "
                    f"{contract.name} failed after {format_elapsed(module_elapsed)}"
                )
                raise

            bar.update(1)
            module_elapsed = perf_counter() - module_start
            emit_runtime_event(
                f"[dataset {dataset_id}] [{module_index}/{len(module_sequence)}] "
                f"{contract.name} completed in {format_elapsed(module_elapsed)}"
            )

    pipeline_elapsed = perf_counter() - pipeline_start
    emit_runtime_event(
        f"[dataset {dataset_id}] pipeline completed in {format_elapsed(pipeline_elapsed)}"
    )

    return planned_modules


def _module_catalog_for_run(config: PipelineConfig) -> tuple[ModuleContract, ...]:
    return tuple(module.describe_module() for module in _module_sequence_for_run(config))


def _module_sequence_for_run(config: PipelineConfig):
    if config.runtime.enable_plots:
        return PIPELINE_MODULES
    return tuple(module for module in PIPELINE_MODULES if module is not plotting)
