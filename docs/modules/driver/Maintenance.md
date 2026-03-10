# Driver Module Maintenance

## Usage notes

- Keep the driver focused on composition, config resolution, and error surfacing.
- If a stage grows complex enough to need branching logic, move that logic back into the stage module.

## Maintenance guidelines

- Re-check this module whenever new stages or optional execution modes are introduced.
- Keep CLI help text consistent with the current module contracts and config fields.

## Operational caveats

- The driver is a common place for hidden methodology drift, especially around default values and stage ordering. Avoid that by importing shared definitions instead of duplicating them.

## Recommendations for future work

- Add run-manifest recording once artefact-producing stages exist.
- Add a tiny end-to-end fixture run once later stages become executable.
