# Driver Module

## Purpose

The `driver` module is the thin orchestration layer for the MVP. It should compose pipeline modules into a reproducible local run without embedding business logic directly in the entrypoint.

## Current scope

This module currently provides a CLI or entrypoint skeleton, config loading, basic module planning, and predictable control flow. It should not implement packet parsing, flow construction, or metric computation itself.

## Inputs

- Pipeline config path.
- Optional module-selection flags or execution controls.

## Outputs

- A resolved run plan or execution context.
- Predictable output locations passed to pipeline modules.
- Clear failure messages when an unimplemented module is requested.

## Methodology and implementation logic

- The driver must remain thin.
- Methodology-relevant behaviour must come from config and shared definitions, not hidden driver logic.
- The driver should preserve the ground-truth-first flow of the pipeline and never let sampled modules run as if they were baseline construction.

## Assumptions and limitations

- The current implementation stops at skeleton validation plus the earliest executable modules; the full end-to-end path is not implemented yet.
- Logging and run metadata may remain minimal until later modules exist.

## Upstream and downstream contracts

- Upstream: `shared`.
- Downstream: `dataset_registry`, `ingest`, `packet_extraction`, `flow_construction`, `sampling`, `metrics`, and `plotting`.
