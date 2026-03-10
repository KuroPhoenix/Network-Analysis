# Sampling Module Maintenance

## Usage notes

- Keep the sampling procedure explicit and reproducible.
- Record seeds whenever randomness is used.
- Keep `packet_index` deterministic because systematic sampling depends on it directly.

## Maintenance guidelines

- Review this module carefully when adding new sampling methods so metadata remains comparable across runs.
- Keep sampling outputs tied to the same dataset, flow key, timeout, and size basis as the baseline.
- Re-check sampled-flow splitting behaviour whenever the flow-reconstruction helper logic changes.

## Operational caveats

- Sampling shortcuts that bypass sampled-packet reconstruction would distort the methodology and should be treated as defects.
- Do not relabel sampled-flow fragments as baseline-matched flows inside this module; that matching belongs to `metrics`.

## Recommendations for future work

- Add more fixture coverage for seeded random sampling once a stable comparison fixture is in place.
- Extend the sampled-packet schema only when downstream metrics or debugging genuinely need extra fields.
