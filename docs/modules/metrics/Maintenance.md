# Metrics Module Maintenance

## Usage notes

- Keep completeness loss and metric distortion distinct in outputs and prose.
- Treat denominator changes or dropped undetected flows as methodology regressions.
- Keep sampled-packet-to-baseline matching deterministic and auditable.

## Maintenance guidelines

- Re-check every formula against the repo documentation before changing this module.
- Re-check zero-duration flows and undefined ratios whenever the rate formulas or size-basis handling changes.

## Operational caveats

- This module is highly sensitive to silent unit drift between packets and bytes.
- This module assumes the baseline-flow time intervals are the authoritative matching windows for sampled packets.

## Recommendations for future work

- Add fixture coverage for `size_basis: both` and seeded random sampling once those scenarios are exercised end to end.
- Revisit whether the summary table should emit extra per-rate diagnostics before expanding the schema further.
