# Runtime Module Maintenance

## Usage notes

- Keep this module focused on dataset-root planning, compatibility adaptation, and dataset-level progress reporting.
- Treat `pipeline.driver` as the only per-dataset composition boundary.
- Prefer adapting config objects here rather than teaching every pipeline module about the active and legacy config surfaces at once.

## Maintenance guidelines

- If the active entrypoint gains new runtime-only controls, add them here first.
- Do not duplicate methodology-sensitive defaults here; they must continue to come from shared config objects.
- Revisit the compatibility adapter when the cache-policy and persisted-manifest slices land.

## Operational caveats

- The current adapter still derives `data/staged` and `data/processed` compatibility roots from the workspace next to `results/`.
- Plotting mode is still mapped onto the legacy boolean plotting gate.
- Any change that makes this module decide baseline, sampling, or metric semantics would be a defect.

## Recommendations for future work

- Add persisted `meta/` and `logs/` outputs when the runtime-manifest slice lands.
- Remove the remaining legacy CLI compatibility path once the canonical v2 entrypoint is fully validated and documented.
