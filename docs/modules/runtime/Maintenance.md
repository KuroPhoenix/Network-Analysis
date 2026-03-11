# Runtime Module Maintenance

## Usage notes

- Keep this module focused on dataset-root planning, compatibility adaptation, and dataset-level progress reporting.
- Treat `pipeline.driver` as the only per-dataset composition boundary.
- Prefer adapting config objects here rather than teaching every pipeline module about the active and legacy config surfaces at once.
- Keep the persisted runtime artefacts lightweight and reproducible. They should describe the run, not replace the metric tables.
- Keep cache retention policy here, not in the metric, flow, or packet modules.

## Maintenance guidelines

- If the active entrypoint gains new runtime-only controls, add them here first.
- Do not duplicate methodology-sensitive defaults here; they must continue to come from shared config objects.
- Revisit the compatibility adapter as the remaining compatibility surfaces are brought onto the same runtime-artifact and cache model.

## Operational caveats

- The active entrypoint now uses hidden cache roots under `.cache/network_analysis/<policy>/...`, but the legacy compatibility paths still derive `data/staged` and `data/processed` roots.
- Plotting mode is still mapped onto the legacy boolean plotting gate.
- Cleanup is only applied after successful active runs. Failed runs intentionally keep their cache for inspection.
- Any change that makes this module decide baseline, sampling, or metric semantics would be a defect.

## Recommendations for future work

- Remove the remaining legacy CLI compatibility path once the canonical v2 entrypoint is fully validated and documented.
- Unify runtime artefacts and cache behaviour across the remaining legacy compatibility surfaces if they are retained for longer.
