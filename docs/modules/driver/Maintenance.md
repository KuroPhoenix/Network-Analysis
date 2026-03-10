# Driver Module Maintenance

## Usage notes

- Keep the driver focused on composition, config resolution, and error surfacing.
- If a module grows complex enough to need branching logic, move that logic back into the module itself.

## Maintenance guidelines

- Re-check this module whenever new modules or optional execution modes are introduced.
- Keep CLI help text consistent with the current module contracts and config fields.
- Keep the runnable module sequence aligned with the actual implemented modules and the `enable_plots` gate.

## Operational caveats

- The driver is a common place for hidden methodology drift, especially around default values and module ordering. Avoid that by importing shared definitions instead of duplicating them.

## Recommendations for future work

- Add run-manifest recording once the repo wants a dedicated execution log beyond module artefacts.
- Revisit plotting orchestration only after the plotting module itself becomes executable.
