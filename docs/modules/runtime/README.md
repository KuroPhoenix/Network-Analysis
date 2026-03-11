# Runtime Module

## Purpose

The `runtime` module is the thin active-architecture orchestration layer that resolves dataset-root execution into one dataset-scoped pipeline run at a time.

It does not implement methodology, metrics, flow reconstruction, or packet parsing logic. It only:

- loads the active v2 dataset-run plan;
- adapts each resolved dataset run into the current executable `PipelineConfig` bridge;
- runs the existing thin driver once per dataset; and
- emits lightweight dataset-level progress and elapsed-time feedback.

## Inputs

- `RunConfig` from `shared.v2_config`
- `DatasetTemplateConfig` from `shared.v2_config`
- the existing driver entrypoint in `pipeline.driver`

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
- The runtime preserves the existing methodology contract by adapting active-architecture resolved dataset runs into the current executable `PipelineConfig` without changing:
  - the `1:1` baseline definition
  - the inactivity timeout
  - the flow key
  - sampling-rate normalization
  - packet-vs-byte labelling
- The runtime currently uses an internal bridge adapter:
  - `results/<dataset>/tables` and `results/<dataset>/plots` are passed through to the current modules
  - active cache roots are resolved under `.cache/network_analysis/<policy>/...`
  - `none` removes dataset-scoped staged and processed cache directories after a successful run
  - `minimal` removes only the staged cache after a successful run and keeps processed intermediates
  - `debug` keeps both staged and processed cache artefacts for inspection
- Plot execution is still controlled by the current boolean module gate. The runtime maps the active `plotting_mode` string onto the existing `runtime.enable_plots` flag without changing plotting semantics.
- The runtime now persists resolved dataset snapshots, run-config snapshots, a run manifest, stage timings, and a plain-text run log for the active entrypoint.

## Upstream and downstream contracts

- Upstream contract:
  - `shared.v2_config` must supply validated active-architecture config objects and resolved dataset runs.
- Downstream contract:
  - `pipeline.driver` remains the only per-dataset module-composition boundary.
  - Future CLI code should treat this module as the active dataset-root runtime boundary rather than duplicating planning logic.

## Assumptions and limitations

- The module is still a bridge layer. It preserves current runnable behaviour while the rest of the repo converges on the v2 architecture.
- Cache policy is enforced on the canonical public entrypoint, but the runtime still maps onto internal bridge config objects for the underlying modules.
- Failed runs keep their cache directories for inspection; the cleanup rules above apply only after successful runs.
