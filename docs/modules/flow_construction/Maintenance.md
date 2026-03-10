# Flow Construction Module Maintenance

## Usage notes

- Treat timeout changes as methodology changes and document them explicitly.
- Keep the flow key stable across baseline and sampled reconstructions unless an experiment explicitly studies another key.

## Maintenance guidelines

- Add targeted tests for boundary cases, especially exactly `15` seconds and greater-than-`15`-second gaps.
- Re-check determinism after any optimisation or chunking change.

## Operational caveats

- This module defines the baseline used by all later comparisons. Errors here invalidate every sampled comparison.

## Recommendations for future work

- Add tiny deterministic fixtures that exercise timeout boundaries and single-packet flows.
- Document the final flow-table schema once implemented.
