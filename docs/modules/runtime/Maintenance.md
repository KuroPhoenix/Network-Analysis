# Runtime Module Maintenance

## Usage notes

- Keep this module focused on dataset-root planning and dataset-level progress reporting.
- Treat `driver` as the only per-dataset composition boundary.
- Prefer keeping runtime-only controls here rather than teaching every pipeline module about them directly.
- Keep the persisted runtime artefacts lightweight and reproducible. They should describe the run, not replace the metric tables.
- Keep cache retention policy here, not in the metric, flow, or packet modules.

## Maintenance guidelines

- If the active entrypoint gains new runtime-only controls, add them here first.
- Do not duplicate methodology-sensitive defaults here; they must continue to come from `config.py`.

## Operational caveats

- The active entrypoint now uses hidden cache roots under `.cache/network_analysis/<policy>/...`.
- Cleanup is only applied after successful active runs. Failed runs intentionally keep their cache for inspection.
- Any change that makes this module decide baseline, sampling, or metric semantics would be a defect.

## Recommendations for future work

- Keep the manifest and log schema stable enough for reproducible reruns and audits.
- Add richer failure summaries only if they remain clearly separated from metric outputs.
