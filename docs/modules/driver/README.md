# Driver Module

## Purpose

The `driver` module is the thin orchestration layer for the MVP. It should compose pipeline modules into a reproducible local run without embedding business logic directly in the entrypoint.

## Current scope

This module now provides the thin runnable entrypoint for the local MVP. It loads config, resolves the module plan, runs the implemented modules end to end, and skips plotting unless `runtime.enable_plots` is enabled.

## Inputs

- Pipeline config path.
- Optional module-selection flags or execution controls.

## Outputs

- A resolved run plan or execution context.
- Predictable output locations passed to pipeline modules.
- Clear failure messages when an unimplemented module is requested.
- End-to-end local execution through metric computation when plotting is disabled.

## Methodology and implementation logic

- The driver must remain thin.
- Methodology-relevant behaviour must come from config and shared definitions, not hidden driver logic.
- The driver should preserve the ground-truth-first flow of the pipeline and never let sampled modules run as if they were baseline construction.

## Assumptions and limitations

- The driver remains intentionally thin; business logic stays inside the pipeline modules.
- Plotting is still optional and remains disabled by default for the local MVP reference path.
- Logging and run metadata remain minimal until a dedicated run-manifest layer is added.

## Upstream and downstream contracts

- Upstream: `shared`.
- Downstream: `dataset_registry`, `ingest`, `packet_extraction`, `flow_construction`, `sampling`, `metrics`, and `plotting`.
