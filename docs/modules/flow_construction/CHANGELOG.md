# Flow Construction Module Changelog

## 2026-03-10

1. Purpose of modification: turn baseline flow construction into an executable local MVP module.
2. What changed: implemented deterministic inactivity-based flow splitting from canonical packet tables, explicit packet and byte accounting, zero-duration handling, and Parquet baseline-flow output.
3. Impact on other pipeline modules: sampling and metrics now have a concrete `1:1` flow table to consume instead of a placeholder contract.
4. Required maintenance or follow-up updates: keep the matching assumptions and schema aligned when sampled-flow reconstruction and metric computation are implemented.
