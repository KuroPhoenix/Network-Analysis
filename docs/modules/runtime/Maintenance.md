# Runtime Module Maintenance

## Usage notes

- Keep this module focused on dataset-root planning, compatibility adaptation, and dataset-level progress reporting.
- Treat `pipeline.driver` as the only per-dataset composition boundary.
- Prefer adapting config objects here rather than teaching every pipeline module about the active and legacy config surfaces at once.
- Keep the persisted runtime artefacts lightweight and reproducible. They should describe the run, not replace the metric tables.

## Maintenance guidelines

- If the active entrypoint gains new runtime-only controls, add them here first.
- Do not duplicate methodology-sensitive defaults here; they must continue to come from shared config objects.
- Revisit the compatibility adapter when the cache-policy slice lands and the remaining compatibility surfaces are brought onto the same runtime-artifact model.

## Operational caveats

- The current adapter still derives `data/staged` and `data/processed` compatibility roots from the workspace next to `results/`.
- Plotting mode is still mapped onto the legacy boolean plotting gate.
- Any change that makes this module decide baseline, sampling, or metric semantics would be a defect.

## Recommendations for future work

- Remove the remaining legacy CLI compatibility path once the canonical v2 entrypoint is fully validated and documented.
- Unify runtime artefacts across the remaining legacy compatibility surfaces if they are retained for longer.
