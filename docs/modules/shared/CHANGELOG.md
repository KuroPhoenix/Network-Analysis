# Shared Module Changelog

## 2026-03-10

1. Purpose of modification: evolve the shared layer from an initial placeholder into the executable contract used by the first local MVP slices.
2. What changed: added explicit byte-basis handling, dataset artifact path resolution, and richer schema definitions for dataset registry, ingest, and packet extraction outputs.
3. Impact on other pipeline modules: dataset discovery, staging, and packet extraction now share one canonical config and artifact-path contract instead of hard-coded paths or hidden defaults.
4. Required maintenance or follow-up updates: keep schema and path definitions aligned with later flow, sampling, and metric implementations as they land.
