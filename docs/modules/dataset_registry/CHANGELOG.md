# Dataset Registry Module Changelog

## 2026-03-10

1. Purpose of modification: turn the dataset registry from a placeholder into the first executable discovery step.
2. What changed: implemented deterministic raw-file discovery, suffix-based capture/compression inference, and Parquet manifest writing with explicit methodology fields.
3. Impact on other pipeline modules: ingest now consumes a persisted registry manifest instead of discovering raw files independently, which keeps raw-file provenance and methodology settings aligned.
4. Required maintenance or follow-up updates: extend the registry to record richer dataset-acceptance metadata once external dataset vetting is integrated.
