# Ingest Module Changelog

## 2026-03-10

### Implementation

1. Purpose of modification: turn ingest into an executable staging step for the local MVP.
2. What changed: implemented deterministic staging for direct captures plus explicit `.gz`, `.xz`, and `.zip` handling, added checksum-backed Parquet ingest manifests, and prefixed staged filenames with deterministic source-order metadata to prevent basename collisions.
3. Impact on other pipeline modules: `packet_extraction` now reads a stable staged-file manifest instead of guessing which raw path or wrapper to parse.
4. Required maintenance or follow-up updates: add broader archive support only if it can remain explicit and reproducible.

### Documentation Audit

1. Purpose of modification: align the ingest docs with the current executable module.
2. What changed: documented the exact manifest schema, deterministic staging rules, supported compression behavior, and the run-order contract with `dataset_registry` and `packet_extraction`.
3. Impact on other pipeline modules: no runtime behavior changed; downstream modules now have clearer documented assumptions about staged files and manifest fields.
4. Required maintenance or follow-up updates: update the docs again if ingest gains new wrappers, staging actions, or manifest columns.
