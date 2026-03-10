# Ingest Module Maintenance

## Usage notes

- Keep raw inputs immutable because later experiments depend on reproducible baseline captures.
- Prefer explicit input directories over ad hoc filenames.
- Expect `.rar` inputs to fail until extra archive tooling is deliberately added.

## Maintenance guidelines

- Keep decompression logic reproducible and free of hidden side effects.
- Update supported formats only when downstream parsing and provenance recording are also updated.
- Preserve checksum coverage when new staging actions are introduced.

## Operational caveats

- Never overwrite raw captures during staging.
- Avoid hiding archive extraction steps inside packet extraction or the driver.
- Multi-member ZIP archives are extracted member by member; collisions should stay deterministic.

## Recommendations for future work

- Revisit richer archive support only after confirming the same provenance and checksum guarantees can be preserved.
- Add explicit cleanup or idempotency policies for repeated staging runs if large datasets are introduced.
