# Driver Module

## Purpose

The `driver` module is the thin orchestration layer for the MVP. It composes named pipeline modules in the repo's canonical local execution order, exposes a dry-run plan, and runs the modules without moving methodology or business logic into the orchestration layer.

## Inputs

- A validated `PipelineConfig` object from `shared.config`
- Module contracts exported by:
  - `dataset_registry`
  - `ingest`
  - `packet_extraction`
  - `flow_construction`
  - `sampling`
  - `metrics`
  - `plotting`

The CLI is responsible for loading the config file path. The driver itself operates on an already-loaded config object.

## Outputs

- A tuple of `PlannedModule` entries from `plan_pipeline`
- A text rendering of the module plan from `render_pipeline_plan`
- A tuple of `PlannedModule` entries returned by `run_pipeline` after executing the selected module sequence
- stderr runtime feedback for local runs, including per-module elapsed times and a pipeline-total elapsed time

The driver does not produce pipeline artefacts directly. The underlying modules write those artefacts to disk.

## Methodology and implementation logic

- Execution order is fixed and ground-truth-first:
  - `dataset_registry`
  - `ingest`
  - `packet_extraction`
  - `flow_construction`
  - `sampling`
  - `metrics`
  - optional `plotting`
- `runtime.enable_plots` is the only module-selection gate in the current MVP. When it is `false`, the plotting module is omitted from both the plan and the run sequence.
- `run_pipeline(..., dry_run=True)` returns the resolved plan without executing any module.
- Runnable local executions emit lightweight per-module elapsed-time logs and a module-count progress bar. This is operational feedback only and must not alter module outputs or metric semantics.
- The driver only composes module calls. Timeout, flow key, sampling semantics, size basis, and matching logic all remain inside shared config and module implementations.

## Upstream and downstream contracts

- Upstream contract:
  - `shared.config` must supply a validated `PipelineConfig`.
  - Each module listed in `PIPELINE_MODULES` must export `describe_module()` and `run_module(config)`.
- Downstream contract:
  - CLI code can treat the driver as the single composition boundary for the local MVP.
  - Module docs and module contracts should stay aligned with the order rendered by the driver.

## Assumptions and limitations

- The current driver has no partial-stage selection beyond the plotting gate.
- The driver returns plan metadata, not a structured run manifest of produced artefacts.
- Logging and execution metadata remain intentionally lightweight in the MVP.
- The driver does not currently persist a structured timing manifest; runtime visibility is terminal-oriented.
- Any future branching logic that affects methodology should stay out of this module unless the repo explicitly changes the orchestration contract.
