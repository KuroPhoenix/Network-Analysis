# Driver Module Maintenance

## Usage notes

- Keep the driver focused on composition, plan rendering, and error surfacing.
- Pass fully validated config objects into the driver. Config-file parsing belongs upstream in the CLI or scripts.
- Use `render_pipeline_plan` when debugging module ordering or output locations.

## Maintenance guidelines

- Keep the execution order aligned with the repo's documented module model.
- If a new module is added, update `PIPELINE_MODULES`, the plan rendering, and the module docs together.
- Keep runtime gating minimal. If orchestration branching grows beyond the plotting toggle, revisit whether some of that logic belongs inside modules instead.
- Keep progress and timing feedback lightweight and stderr-oriented so plan output and machine-readable artifacts stay clean.

## Operational caveats

- The driver is a common place for hidden methodology drift. Avoid duplicating timeout, flow-key, sampling-rate, or unit logic here.
- `run_pipeline` returns plan metadata only. Callers that need artefact paths must resolve them through module contracts or shared artifact helpers.
- Any discrepancy between the plan view and the executed module sequence should be treated as a defect.
- Timing feedback is observational only. Do not let retries, branching, or sampling logic depend on elapsed-time output.

## Recommendations for future work

- Add a structured run manifest only if the repo needs stronger execution auditing than module artefacts and Git history already provide.
- Revisit partial-stage execution only if it can be added without encouraging sampled-only runs that bypass baseline construction.
