# Driver Module Maintenance

## Usage notes

- Keep the driver focused on composition, plan rendering, and error surfacing.
- Pass fully validated config objects into the driver. Config-file parsing belongs upstream in the CLI or scripts.
- Use `render_pipeline_plan` when debugging module ordering or output locations.
- Treat the optional runtime observer as a thin visibility hook, not as a place to add orchestration policy.

## Maintenance guidelines

- Keep the execution order aligned with the repo's documented module model.
- If a new module is added, update `PIPELINE_MODULES`, the plan rendering, and the module docs together.
- Keep runtime gating minimal. If orchestration branching grows beyond the plotting toggle, revisit whether some of that logic belongs inside modules instead.
- If the observer event schema changes, update runtime consumers and driver docs in the same slice.

## Operational caveats

- The driver is a common place for hidden methodology drift. Avoid duplicating timeout, flow-key, sampling-rate, or unit logic here.
- `run_pipeline` returns plan metadata only. Callers that need artefact paths must resolve them through module contracts or shared artifact helpers.
- The observer callback should remain side-effect free from the driver's perspective; persistence policy belongs in runtime code.
- Any discrepancy between the plan view and the executed module sequence should be treated as a defect.

## Recommendations for future work

- Keep persisted run manifests and logs in the runtime layer rather than broadening the driver's responsibility.
- Revisit partial-stage execution only if it can be added without encouraging sampled-only runs that bypass baseline construction.
