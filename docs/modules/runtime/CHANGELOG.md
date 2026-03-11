# Runtime Module Changelog

## 2026-03-11

1. Purpose of modification: introduce the canonical dataset-root runtime boundary required by the active architecture.
2. What changed: added a thin `runtime` adapter that resolves dataset-root runs from `dataset_template.yaml` and `run_conf.yaml`, renders active execution plans, and executes one dataset-scoped driver run at a time.
3. Impact on other pipeline modules: no methodology logic moved; the existing driver and module sequence remain unchanged, but the repo now has a canonical active entry surface over them.
4. Required maintenance or follow-up updates: remove or reduce legacy CLI compatibility paths after the remaining config, output, and cache migrations land.
