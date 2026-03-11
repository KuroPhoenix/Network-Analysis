# Driver Module Changelog

## 2026-03-11

1. Purpose of modification: expose a thin runtime-observer hook without moving logging or manifest policy into the driver.
2. What changed: added `ModuleRuntimeEvent` and an optional `observer` callback on `run_pipeline`, emitting per-module start, completion, and failure timing events while preserving the fixed module order and plotting gate.
3. Impact on other pipeline modules: runtime code can now persist stage timings and progress logs without changing module methodology or artefact semantics.
4. Required maintenance or follow-up updates: keep observer consumers and driver documentation aligned if the event schema or module sequence changes.

## 2026-03-10

### Implementation

1. Purpose of modification: turn the thin driver into a runnable local MVP entrypoint.
2. What changed: wired the implemented modules into the CLI run path, kept planning output aligned with the actual runnable module set, and made plotting conditional on `runtime.enable_plots`.
3. Impact on other pipeline modules: the full local path from raw captures through metrics now runs under one thin orchestration layer without moving business logic into the driver.
4. Required maintenance or follow-up updates: update this module documentation when module execution order, optional plotting behaviour, or run metadata changes.

### Documentation Audit

1. Purpose of modification: align driver docs with the actual orchestration interface.
2. What changed: clarified that the driver consumes `PipelineConfig`, returns plan metadata rather than artefacts, and currently supports only the plotting gate as execution-time module selection.
3. Impact on other pipeline modules: no runtime behavior changed; CLI and module-doc integration points are now clearer.
4. Required maintenance or follow-up updates: update the docs if the driver gains partial-stage execution, richer run metadata, or a different module order.
