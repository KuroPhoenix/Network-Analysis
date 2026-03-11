# Shared Module Changelog

## 2026-03-12

1. Purpose of modification: align shared configuration contracts with the active public architecture.
2. What changed: removed the public legacy batch-config surface from the repo, kept `dataset_template.yaml` plus `run_conf.yaml` as the only documented public config pair, and reclassified the older `PipelineConfig` loader as internal bridge machinery.
3. Impact on other pipeline modules: the runtime and docs now share one public config story, while module-level tests can still use the internal bridge config until later refactor slices remove it.
4. Required maintenance or follow-up updates: continue reducing internal bridge-only config code as driver and module boundaries become more native to the active runtime.

## 2026-03-11

1. Purpose of modification: introduce the first active-architecture config scaffolding without changing the current MVP runtime entrypoints.
2. What changed: added shared support for loading `configs/dataset_template.yaml` and `configs/run_conf.yaml`, introduced a v2 dataset-resolution layer, and added a cache-policy type for the active architecture.
3. Impact on other pipeline modules: no module semantics changed yet, but future entrypoint work can now resolve dataset-scoped runs without inventing a separate public config model.
4. Required maintenance or follow-up updates: keep the active public config layer aligned with any remaining internal bridge config structures until those bridge surfaces are flattened.

## 2026-03-10

1. Purpose of modification: keep the shared contract aligned with the executable sampling and metrics modules.
2. What changed: extended the shared artifact paths and schema definitions to cover sampled-packet tables, sampled-flow tables, the sampling manifest, and the metric summary and per-flow metric outputs.
3. Impact on other pipeline modules: sampling, metrics, and the driver now share one explicit artefact contract instead of inventing per-rate paths or output columns ad hoc.
4. Required maintenance or follow-up updates: keep schema and path definitions aligned if new sampling methods, new size estimators, or extra result diagnostics are added.
