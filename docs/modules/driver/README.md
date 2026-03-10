# Driver Module

## Purpose

The `driver` module is the thin orchestration layer for the MVP. It should compose stage modules into a reproducible local run without embedding stage logic directly in the entrypoint.

## Stage 1 scope

At Stage 1, this module is expected to provide a CLI or entrypoint skeleton, config loading, basic stage selection, and predictable control flow. It should not implement packet parsing, flow construction, or metric computation itself.

## Inputs

- Pipeline config path.
- Optional stage-selection flags or execution controls.

## Outputs

- A resolved run plan or execution context.
- Predictable output locations passed to stage modules.
- Clear failure messages when an unimplemented stage is requested.

## Methodology and implementation logic

- The driver must remain thin.
- Methodology-relevant behaviour must come from config and shared definitions, not hidden driver logic.
- The driver should preserve the ground-truth-first flow of the pipeline and never let sampled stages run as if they were baseline construction.

## Assumptions and limitations

- Stage 1 should stop at skeleton validation; end-to-end data processing is not implemented yet.
- Logging and run metadata may remain minimal until later stages exist.

## Upstream and downstream contracts

- Upstream: `shared`.
- Downstream: `dataset_registry`, `ingest`, `packet_extraction`, `flow_construction`, `sampling`, `metrics`, and `plotting`.
