# Metrics Module Maintenance

## Usage notes

- Keep completeness loss and metric distortion distinct in outputs and prose.
- Treat denominator changes or dropped undetected flows as methodology regressions.

## Maintenance guidelines

- Re-check every formula against the repo documentation before changing this module.
- Add focused tests for zero-duration flows and undefined ratios as soon as implementation begins.

## Operational caveats

- This module is highly sensitive to silent unit drift between packets and bytes.

## Recommendations for future work

- Add fixture-based tests for matching, detection denominator correctness, and derived metric formulas.
- Document exact output schemas once the first implementation lands.
