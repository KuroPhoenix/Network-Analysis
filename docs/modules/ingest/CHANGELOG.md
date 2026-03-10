# Ingest Module Changelog

## 2026-03-10

1. Purpose of modification: document the ingest-stage contract for the Stage 1 skeleton.
2. What changed: added initial documentation for raw-file discovery, immutable staging, and explicit decompression expectations.
3. Impact on other modules or pipeline stages: packet extraction can later depend on a stable staged-file manifest instead of raw path guessing.
4. Required maintenance or follow-up updates: update this documentation when supported archive formats, manifests, or checksum behaviour are implemented.
