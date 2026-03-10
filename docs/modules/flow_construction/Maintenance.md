# Flow Construction Module Maintenance

## Usage notes

- Treat timeout changes as methodology changes and document them explicitly.
- Keep the flow key stable across baseline and sampled reconstructions unless an experiment explicitly studies another key.
- Re-run boundary tests whenever flow ordering, key grouping, or timestamp handling changes.
- Keep the canonical microsecond bounds and the human-readable datetime bounds in sync.

## Maintenance guidelines

- Add targeted tests for boundary cases, especially exactly `15` seconds and greater-than-`15`-second gaps.
- Re-check determinism after any optimisation or chunking change.
- Keep zero-duration flow handling explicit. Do not silently replace undefined sending rates with zero.

## Operational caveats

- This module defines the baseline used by all later comparisons. Errors here invalidate every sampled comparison.
- Matching downstream sampled flows by `flow_id` alone is not valid because sampled reconstruction must be derived independently from sampled packets.

## Recommendations for future work

- Add tiny deterministic fixtures that exercise timeout boundaries and single-packet flows.
- Extend byte accounting only when the alternative byte definition is made explicit in shared config and documentation.
