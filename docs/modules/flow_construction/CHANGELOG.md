# Flow Construction Module Changelog

## 2026-03-10

### Implementation

1. Purpose of modification: turn baseline flow construction into an executable local MVP module.
2. What changed: implemented deterministic inactivity-based flow splitting from canonical packet tables, explicit packet and byte accounting, canonical start and end microsecond bounds, zero-duration handling, and Parquet baseline-flow output.
3. Impact on other pipeline modules: `sampling` and `metrics` now have a concrete `1:1` flow table to consume instead of a placeholder contract.
4. Required maintenance or follow-up updates: keep the matching assumptions and schema aligned when sampled-flow reconstruction and metric computation are implemented.

### Documentation Audit

1. Purpose of modification: align flow-construction docs with the implemented baseline semantics.
2. What changed: documented the required packet schema, exact timeout-splitting rule, deterministic flow-ID assignment, and the downstream dependency on baseline intervals rather than sampled-flow IDs.
3. Impact on other pipeline modules: no runtime behavior changed; baseline-flow contracts are now clearer for `sampling` and `metrics`.
4. Required maintenance or follow-up updates: update the docs whenever timeout logic, byte basis support, or output columns change.
