# Runtime Module

## Purpose

The `runtime` module is the thin active-architecture orchestration layer that resolves dataset-root execution into one dataset-scoped pipeline run at a time.

It does not implement methodology, metrics, flow reconstruction, or packet parsing logic. It only:

- loads the active v2 dataset-run plan;
- adapts each resolved dataset run into the current executable `PipelineConfig`;
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

The module does not write analysis artefacts directly. Downstream pipeline modules still write packet, flow, metric, and plot artefacts.

## Methodology and implementation logic

- Dataset-root discovery is deterministic and produces one run per discovered dataset folder.
- The runtime preserves the existing methodology contract by adapting active-architecture resolved dataset runs into the current executable `PipelineConfig` without changing:
  - the `1:1` baseline definition
  - the inactivity timeout
  - the flow key
  - sampling-rate normalization
  - packet-vs-byte labelling
- The runtime currently uses a compatibility adapter:
  - `results/<dataset>/tables` and `results/<dataset>/plots` are passed through to the current modules
  - `data/staged` and `data/processed` are still derived as compatibility roots until the cache-policy slice lands
- Because plotting still uses the legacy artifact helper, the final SVG path currently includes one extra dataset-id leaf under the dataset plot root.
- Plot execution is still controlled by the current boolean module gate. The runtime maps the active `plotting_mode` string onto the existing `runtime.enable_plots` flag without changing plotting semantics.

## Upstream and downstream contracts

- Upstream contract:
  - `shared.v2_config` must supply validated active-architecture config objects and resolved dataset runs.
- Downstream contract:
  - `pipeline.driver` remains the only per-dataset module-composition boundary.
  - Future CLI code should treat this module as the active dataset-root runtime boundary rather than duplicating planning logic.

## Assumptions and limitations

- The module is still a bridge layer. It preserves current runnable behaviour while the rest of the repo converges on the v2 architecture.
- Persisted `meta/` and `logs/` outputs are not implemented yet.
- Cache policy is parsed but not yet enforced in runtime execution.
- Legacy CLI compatibility paths still exist alongside this module and should be retired in a later slice.
