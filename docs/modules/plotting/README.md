# Plotting Module

## Purpose

The `plotting` module will turn metric tables into minimal reproducible visual outputs that demonstrate the pipeline is working end to end.

## Current scope

This module is now implemented as a lightweight SVG plot writer for the active architecture. It consumes the existing metric summary and per-flow metric tables, writes deterministic static figures under the dataset plot directory, and emits a plotting-summary parquet that records the per-rate values used by the line plots.

## Inputs

- Metric tables from `metrics`.
- Plot selection or enablement settings from config.

## Outputs

- Static SVG figure files under `results/<dataset_id>/plots/`.
- `plotting_summary.parquet` under the same plot directory.
- One detection-rate line plot.
- Per-rate line plots for:
  - packet size estimation
  - byte size estimation
  - duration
  - packet sending rate
  - byte sending rate
- Empirical-CDF plots for:
  - packet size overestimation factor
  - byte size overestimation factor
  - duration underestimation factor
  - packet sending rate overestimation factor
  - byte sending rate overestimation factor

## Methodology and implementation logic

- Plotting is downstream of metric computation and must not redefine the measured values.
- Labels should make the dataset, sampling rate, baseline condition, and size basis explicit where relevant.
- Plotting remains secondary to correctness and reproducibility.
- Detection rate is plotted directly from `metric_summary`.
- The remaining per-rate line plots summarise `flow_metrics` with a documented aggregation:
  - median over detected-flow rows with defined values for the plotted metric
- Duration-based plots prefer `packets` rows when both packet and byte bases are present, because duration is basis-independent and duplicate rows would otherwise repeat the same values.
- The factor plots render empirical CDFs from defined detected-flow rows in `flow_metrics`.
- The `1:1` point remains labeled as the ground-truth baseline in the rate-line SVGs.
- `plotting_summary.parquet` records the exact per-rate values used by the line plots so the figures remain traceable back to stored metric rows.

## Assumptions and limitations

- The plot layer remains intentionally lightweight and SVG-only.
- CDF plots use all defined detected-flow rows for the relevant factor and therefore do not collapse the factor distributions into a single line-plot aggregate.
- If a requested size basis is absent from `flow_metrics`, the corresponding size- or rate-specific figure is skipped rather than invented from the other basis.

## Upstream and downstream contracts

- Upstream: `metrics`, `shared`.
- Downstream: result summaries and report-ready outputs.
