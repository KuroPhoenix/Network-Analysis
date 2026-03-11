"""Thin driver that composes the pipeline modules."""

from dataclasses import dataclass
from time import perf_counter
from typing import Callable

from . import (
    dataset_registry,
    flow_construction,
    ingest,
    metrics,
    packet_extraction,
    plotting,
    sampling,
)
from .base import ModuleContract
from .config import DatasetRunConfig

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


@dataclass(frozen=True)
class ModuleRuntimeEvent:
    """A timing event emitted around one module execution."""

    dataset_id: str
    module_name: str
    module_index: int
    module_total: int
    status: str
    elapsed_seconds: float | None = None


def get_module_catalog() -> tuple[ModuleContract, ...]:
    """Return the named module catalog in execution order."""

    return tuple(module.describe_module() for module in PIPELINE_MODULES)


def plan_pipeline(config: DatasetRunConfig) -> tuple[PlannedModule, ...]:
    """Build a dry-run execution plan from the configured module catalog."""

    return tuple(
        PlannedModule(contract=contract, resolved_outputs=contract.resolve_output_paths(config))
        for contract in _module_catalog_for_run(config)
    )


def render_pipeline_plan(config: DatasetRunConfig) -> str:
    """Render the pipeline plan for CLI output."""

    lines = [
        "Pipeline module plan",
        f"Dataset: {config.dataset.dataset_id}",
        f"Sampling rates: {', '.join(f'1:{rate}' for rate in config.sampling.normalized_rates())}",
        f"Flow key: {', '.join(config.methodology.flow_key_fields)}",
        f"Inactivity timeout: {config.methodology.inactivity_timeout_seconds}s",
        f"Size basis: {config.methodology.size_basis}",
        f"Byte basis: {config.methodology.byte_basis}",
        f"Plotting mode: {config.runtime.plotting_mode}",
        "",
    ]
    for module in plan_pipeline(config):
        lines.append(f"{module.contract.name}: {module.contract.description}")
        for output in module.resolved_outputs:
            lines.append(f"  output -> {output}")
    return "\n".join(lines)


def run_pipeline(
    config: DatasetRunConfig,
    *,
    dry_run: bool = False,
    observer: Callable[[ModuleRuntimeEvent], None] | None = None,
) -> tuple[PlannedModule, ...]:
    """Run or dry-run the pipeline using the pipeline modules."""

    planned_modules = plan_pipeline(config)
    if dry_run:
        return planned_modules

    module_sequence = _module_sequence_for_run(config)
    dataset_id = config.dataset.dataset_id
    for module_index, module in enumerate(module_sequence, start=1):
        contract = module.describe_module()
        if observer is not None:
            observer(
                ModuleRuntimeEvent(
                    dataset_id=dataset_id,
                    module_name=contract.name,
                    module_index=module_index,
                    module_total=len(module_sequence),
                    status="starting",
                )
            )
        module_start = perf_counter()
        try:
            module.run_module(config)
        except BaseException:
            if observer is not None:
                observer(
                    ModuleRuntimeEvent(
                        dataset_id=dataset_id,
                        module_name=contract.name,
                        module_index=module_index,
                        module_total=len(module_sequence),
                        status="failed",
                        elapsed_seconds=perf_counter() - module_start,
                    )
                )
            raise

        if observer is not None:
            observer(
                ModuleRuntimeEvent(
                    dataset_id=dataset_id,
                    module_name=contract.name,
                    module_index=module_index,
                    module_total=len(module_sequence),
                    status="completed",
                    elapsed_seconds=perf_counter() - module_start,
                )
            )

    return planned_modules


def _module_catalog_for_run(config: DatasetRunConfig) -> tuple[ModuleContract, ...]:
    return tuple(module.describe_module() for module in _module_sequence_for_run(config))


def _module_sequence_for_run(config: DatasetRunConfig):
    if config.runtime.plots_enabled():
        return PIPELINE_MODULES
    return tuple(module for module in PIPELINE_MODULES if module is not plotting)
