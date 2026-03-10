# Metrics Module

## Purpose

The `metrics` module will compare sampled outputs against the `1:1` baseline and compute completeness and distortion metrics for each sampling rate.

## Stage 1 scope

At Stage 1, this module is a documented placeholder. Matching logic and metric computation are not implemented yet.

## Inputs

- Baseline flow tables from `flow_construction`.
- Sampled flow tables from `sampling`.
- Explicit flow key, timeout, and size basis definitions from `shared`.

## Outputs

- Summary tables for detection results by sampling rate.
- Per-flow metric tables containing baseline values, sampled values, ratio metrics, and detection status.

## Methodology and implementation logic

- Every sampled result must be matched directly against the `1:1` baseline.
- Undetected baseline flows must remain in the detection denominator.
- Units must remain explicit, especially when packet-based and byte-based metrics both exist.
- Undefined ratio or rate cases should be represented explicitly rather than hidden.

## Assumptions and limitations

- Stage 1 does not yet define the exact matching algorithm or output schema fields in code.
- Derived metrics must stay aligned with the repository formulas once implemented.

## Upstream and downstream contracts

- Upstream: `flow_construction`, `sampling`, `shared`.
- Downstream: `plotting` and result-writing workflows.
