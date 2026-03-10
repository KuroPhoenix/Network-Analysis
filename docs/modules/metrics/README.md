# Metrics Module

## Purpose

The `metrics` module will compare sampled outputs against the `1:1` baseline and compute completeness and distortion metrics for each sampling rate.

## Current scope

This module is now implemented for the local CPU reference path. It reads the fixed `1:1` baseline flow table plus the sampling manifest, maps sampled packets back to baseline flows using the shared directional 5-tuple and baseline time interval, and writes Parquet summary and per-flow metric tables.

## Inputs

- Baseline flow tables from `flow_construction`.
- Sampled packet tables and the sampling manifest from `sampling`.
- Explicit flow key, timeout, and size basis definitions from `shared`.

## Outputs

- Summary tables for detection results by sampling rate.
- Per-flow metric tables containing baseline values, sampled values, ratio metrics, and detection status.

## Methodology and implementation logic

- Every sampled result must be matched directly against the `1:1` baseline.
- Undetected baseline flows must remain in the detection denominator.
- Units must remain explicit, especially when packet-based and byte-based metrics both exist.
- Undefined ratio or rate cases should be represented explicitly rather than hidden.
- Sampled-flow tables remain diagnostic outputs. The metric computation itself uses sampled packets matched back to baseline flow intervals so every baseline flow has one direct comparison row per sampling rate and size basis.

## Assumptions and limitations

- Matching currently assumes baseline flows sharing the same directional 5-tuple do not overlap in time, which is guaranteed by the inactivity-based baseline construction.
- Per-flow metrics are emitted once per sampling rate and once per requested size basis.
- Derived metrics stay aligned with the repository formulas and keep undefined cases explicit.

## Upstream and downstream contracts

- Upstream: `flow_construction`, `sampling`, `shared`.
- Downstream: `plotting` and result-writing workflows.
