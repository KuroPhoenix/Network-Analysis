# Dataset Registry Module Maintenance

## Usage notes

- Keep dataset identifiers stable because they propagate into processed artefacts and result filenames.
- Expect one registry row per discovered raw file, not one row per dataset.
- Record uncertainty explicitly when source metadata is incomplete.

## Maintenance guidelines

- Keep discovery deterministic; if glob handling changes, preserve a stable sort order.
- Update this module when new dataset-level metadata becomes necessary for downstream reproducibility.
- Review the contract against ingest whenever supported archive or capture formats expand.

## Operational caveats

- Do not let convenience shortcuts turn sampled datasets into baseline inputs.
- Avoid embedding dataset acceptance policy in multiple modules.
- Do not silently infer missing suffix information for unsupported files.

## Recommendations for future work

- Add structured validation for capture format, provenance, and acceptance-rule reporting.
- Add richer provenance fields such as capture year or documented timestamp quality when dataset vetting is wired in.
