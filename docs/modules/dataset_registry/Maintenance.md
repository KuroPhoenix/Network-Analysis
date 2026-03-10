# Dataset Registry Module Maintenance

## Usage notes

- Keep dataset identifiers stable because they should propagate into processed artefacts and result filenames.
- Record uncertainty explicitly when source metadata is incomplete.

## Maintenance guidelines

- Update this module when new dataset-level metadata becomes necessary for downstream reproducibility.
- Review the contract against ingest whenever supported archive or capture formats expand.

## Operational caveats

- Do not let convenience shortcuts turn sampled datasets into baseline inputs.
- Avoid embedding dataset acceptance policy in multiple modules.

## Recommendations for future work

- Add structured validation for capture format, provenance, and acceptance-rule reporting.
- Add manifest persistence once ingest produces staged outputs.
