# Runtime Module Maintenance

## Usage notes

- Keep this module focused on dataset-root planning, compatibility adaptation, and dataset-level progress reporting.
- Treat `pipeline.driver` as the only per-dataset composition boundary.
- Prefer adapting active runtime config objects here rather than teaching every pipeline module about runtime-only controls directly.
- Keep the persisted runtime artefacts lightweight and reproducible. They should describe the run, not replace the metric tables.
- Keep cache retention policy here, not in the metric, flow, or packet modules.

## Maintenance guidelines

- If the active entrypoint gains new runtime-only controls, add them here first.
- Do not duplicate methodology-sensitive defaults here; they must continue to come from shared config objects.
- Revisit the bridge adapter as the module interfaces converge further on the native v2 runtime model.

## Operational caveats

- The active entrypoint now uses hidden cache roots under `.cache/network_analysis/<policy>/...`.
- Plotting mode is still mapped onto the current boolean plotting gate.
- Cleanup is only applied after successful active runs. Failed runs intentionally keep their cache for inspection.
- Any change that makes this module decide baseline, sampling, or metric semantics would be a defect.

## Recommendations for future work

- Replace the remaining plotting gate bridge once plotting follows the native runtime model more directly.
- Flatten the internal bridge config if later refactor slices remove the need for a separate executable `PipelineConfig`.
