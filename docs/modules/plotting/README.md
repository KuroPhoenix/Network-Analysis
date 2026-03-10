# Plotting Module

## Purpose

The `plotting` module will turn metric tables into minimal reproducible visual outputs that demonstrate the pipeline is working end to end.

## Current scope

This module is now implemented as a lightweight SVG plot writer for the local MVP. It consumes the existing metric summary table and renders a deterministic flow-detection-rate graph without changing any metric semantics or adding a heavy plotting dependency.

## Inputs

- Metric tables from `metrics`.
- Plot selection or enablement settings from config.

## Outputs

- Static SVG figure files under `results/plots/{dataset_id}/`.
- A minimal detection-rate graph derived directly from the metric summary output.

## Methodology and implementation logic

- Plotting is downstream of metric computation and must not redefine the measured values.
- Labels should make the dataset, sampling rate, baseline condition, and size basis explicit where relevant.
- Plotting remains secondary to correctness and reproducibility.
- The current MVP plot uses `metric_summary` rows, prefers the `packets` size-basis rows when present, and draws `flow_detection_rate` directly against the configured `1:X` sampling rates.
- The `1:1` point remains labeled as the ground-truth baseline in the rendered SVG.

## Assumptions and limitations

- The current module renders one SVG plot: flow detection rate vs sampling rate.
- If both packet and byte size bases are present, the detection-rate plot uses the `packets` rows because detection rate itself is basis-independent and that avoids duplicate points.
- The plot layer is intentionally minimal and does not yet render distortion-factor distributions or multiple figure styles.

## Upstream and downstream contracts

- Upstream: `metrics`, `shared`.
- Downstream: result summaries and report-ready outputs.
