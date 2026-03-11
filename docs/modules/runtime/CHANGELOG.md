# Runtime Module Changelog

## 2026-03-11

1. Purpose of modification: make the active cache-policy contract executable without changing methodology or module formulas.
2. What changed: moved the active runtime’s staged and processed artefacts under `.cache/network_analysis/<policy>/...`, made `none`, `minimal`, and `debug` control post-run cache retention, and recorded final cache state in the runtime manifest.
3. Impact on other pipeline modules: the active entrypoint no longer depends on `data/staged` and `data/processed`, but the underlying modules still consume the same resolved `PipelineConfig` paths and write the same metric and plot outputs.
4. Required maintenance or follow-up updates: either retire the legacy compatibility surfaces or bring them onto the same cache model so the repo stops carrying two storage behaviours.

## 2026-03-11

1. Purpose of modification: introduce the canonical dataset-root runtime boundary required by the active architecture.
2. What changed: added a thin `runtime` adapter that resolves dataset-root runs from `dataset_template.yaml` and `run_conf.yaml`, renders active execution plans, executes one dataset-scoped driver run at a time, and persists runtime artefacts under `meta/` and `logs/`.
3. Impact on other pipeline modules: no methodology logic moved; the existing driver and module sequence remain unchanged, but the repo now has a canonical active entry surface with persisted runtime provenance.
4. Required maintenance or follow-up updates: remove or reduce legacy CLI compatibility paths after the remaining config, output, and cache migrations land, and unify persisted runtime artefacts across those remaining compatibility paths.
