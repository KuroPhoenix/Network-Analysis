# Runtime Module

## Purpose

The `runtime` module is the thin active-architecture orchestration layer that resolves dataset-root execution into one dataset-scoped pipeline run at a time.

It does not implement methodology, metrics, flow reconstruction, or packet parsing logic. It only:

- loads the active v2 dataset-run plan;
- resolves each discovered dataset into one executable per-dataset run config;
- runs the existing thin driver once per dataset; and
- emits lightweight dataset-level progress and elapsed-time feedback.

## Inputs

- `RunConfig` from `config`
- `DatasetTemplateConfig` from `config`
- the thin driver entrypoint in `driver`

## Outputs

- a tuple of `PlannedDatasetRun` objects from `plan_active_runs`
- a text rendering of the dataset-root execution plan from `render_active_plan`
- dataset-level stderr runtime feedback during execution
- persisted runtime artefacts under `results/<dataset>/meta/` and `results/<dataset>/logs/`, including:
  - `resolved_dataset.yaml`
  - `run_config.yaml`
  - `run_manifest.json`
  - `stage_timings.json`
  - `run.log`

The module does not write packet, flow, metric, or plot artefacts directly. Downstream pipeline modules still write those analysis outputs.

## Methodology and implementation logic

- Dataset-root discovery is deterministic and produces one run per discovered dataset folder.
- The runtime preserves the existing methodology contract by resolving active-architecture dataset runs directly into executable per-dataset configs without changing:
  - the `1:1` baseline definition
  - the inactivity timeout
  - the flow key
  - sampling-rate normalization
  - packet-vs-byte labelling
- Active cache roots are resolved under `.cache/network_analysis/<policy>/...`
- `none` removes dataset-scoped staged and processed cache directories after a successful run
- `minimal` removes only the staged cache after a successful run and keeps processed intermediates
- `debug` keeps both staged and processed cache artefacts for inspection
- Plot execution follows `runtime.plotting_mode` directly through the per-dataset runtime config.
- The runtime now persists resolved dataset snapshots, run-config snapshots, a run manifest, stage timings, and a plain-text run log for the active entrypoint.

## Upstream and downstream contracts

- Upstream contract:
  - `config` must supply validated active-architecture config objects and resolved dataset runs.
- Downstream contract:
  - `driver` remains the only per-dataset module-composition boundary.
  - Future CLI code should treat this module as the active dataset-root runtime boundary rather than duplicating planning logic.

## Assumptions and limitations

- The runtime is intentionally thin. It should stay responsible for planning, run-state persistence, and cache retention rather than module-level methodology.
- Failed runs keep their cache directories for inspection; the cleanup rules above apply only after successful runs.
