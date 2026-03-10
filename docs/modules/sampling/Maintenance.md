# Sampling Module Maintenance

## Usage notes

- Keep the sampling procedure explicit and reproducible.
- Record seeds whenever randomness is used.

## Maintenance guidelines

- Review this module carefully when adding new sampling methods so metadata remains comparable across runs.
- Keep sampling outputs tied to the same dataset, flow key, timeout, and size basis as the baseline.

## Operational caveats

- Sampling shortcuts that bypass sampled-packet reconstruction would distort the methodology and should be treated as defects.

## Recommendations for future work

- Add deterministic fixture tests for `1:1` and at least one `1:X` path.
- Document the sampled-flow schema when implementation begins.
