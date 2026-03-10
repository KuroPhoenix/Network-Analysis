# Ingest Module Changelog

## 2026-03-10

1. Purpose of modification: turn ingest into an executable staging step for the local MVP.
2. What changed: implemented deterministic staging for direct captures plus explicit `.gz`, `.xz`, and `.zip` handling, and added checksum-backed Parquet ingest manifests.
3. Impact on other pipeline modules: packet extraction now reads a stable staged-file manifest instead of guessing which raw path or wrapper to parse.
4. Required maintenance or follow-up updates: add broader archive support only if it can remain explicit and reproducible.
