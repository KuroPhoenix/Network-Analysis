# Runtime Module Changelog

## 2026-03-12

1. Purpose of modification: make the runtime the sole public execution boundary required by the active architecture.
2. What changed: removed the public legacy CLI and batch execution surfaces, leaving the dataset-root runtime as the only documented entrypoint while keeping the internal `PipelineConfig` bridge for module execution.
3. Impact on other pipeline modules: runtime now owns the only public run path, but no baseline, sampling, metrics, or unit semantics changed.
4. Required maintenance or follow-up updates: continue reducing the internal bridge layer so plotting and later runtime controls no longer need boolean-era adaptations.

## 2026-03-11

1. Purpose of modification: make the active cache-policy contract executable without changing methodology or module formulas.
2. What changed: moved the active runtime’s staged and processed artefacts under `.cache/network_analysis/<policy>/...`, made `none`, `minimal`, and `debug` control post-run cache retention, and recorded final cache state in the runtime manifest.
3. Impact on other pipeline modules: the active entrypoint no longer depends on `data/staged` and `data/processed`, but the underlying modules still consume the same resolved `PipelineConfig` paths and write the same metric and plot outputs.
4. Required maintenance or follow-up updates: keep cache behaviour aligned with the active runtime as the remaining internal bridge layer is flattened further.

## 2026-03-11

1. Purpose of modification: introduce the canonical dataset-root runtime boundary required by the active architecture.
2. What changed: added a thin `runtime` adapter that resolves dataset-root runs from `dataset_template.yaml` and `run_conf.yaml`, renders active execution plans, executes one dataset-scoped driver run at a time, and persists runtime artefacts under `meta/` and `logs/`.
3. Impact on other pipeline modules: no methodology logic moved; the existing driver and module sequence remain unchanged, but the repo now has a canonical active entry surface with persisted runtime provenance.
4. Required maintenance or follow-up updates: keep runtime provenance aligned with the canonical dataset-root entrypoint as later refactor slices simplify plotting and package boundaries.
