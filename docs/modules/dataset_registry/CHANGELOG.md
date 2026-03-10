# Dataset Registry Module Changelog

## 2026-03-10

### Runtime and Format Detection

1. Purpose of modification: make raw-capture discovery robust against mislabeled `.pcap` and `.pcapng` suffixes without changing methodology.
2. What changed: replaced suffix-only capture-format inference with header-based detection for directly readable captures and single-stream wrappers such as `.gz` and `.xz`, while retaining the existing deterministic registry manifest contract.
3. Impact on other pipeline modules: `ingest` and `packet_extraction` now receive the correct capture-format hint for datasets such as the current ONU captures whose filename suffix does not match the actual capture header.
4. Required maintenance or follow-up updates: if archive-member inspection becomes necessary for `.zip` or other wrappers, extend this behavior explicitly rather than falling back to silent guessing.

1. Purpose of modification: turn the dataset registry from a placeholder into the first executable discovery step.
2. What changed: implemented deterministic raw-file discovery, capture/compression inference, and Parquet manifest writing with explicit methodology fields.
3. Impact on other pipeline modules: ingest now consumes a persisted registry manifest instead of discovering raw files independently, which keeps raw-file provenance and methodology settings aligned.
4. Required maintenance or follow-up updates: extend the registry to record richer dataset-acceptance metadata once external dataset vetting is integrated.
