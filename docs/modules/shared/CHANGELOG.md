# Shared Module Changelog

## 2026-03-10

1. Purpose of modification: keep the shared contract aligned with the executable sampling and metrics modules.
2. What changed: extended the shared artifact paths and schema definitions to cover sampled-packet tables, sampled-flow tables, the sampling manifest, and the metric summary and per-flow metric outputs.
3. Impact on other pipeline modules: sampling, metrics, and the driver now share one explicit artefact contract instead of inventing per-rate paths or output columns ad hoc.
4. Required maintenance or follow-up updates: keep schema and path definitions aligned if new sampling methods, new size estimators, or extra result diagnostics are added.
