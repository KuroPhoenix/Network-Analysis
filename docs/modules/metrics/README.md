# Metrics Module

## Purpose

The `metrics` module compares every sampled run directly against the fixed `1:1` baseline and writes the completeness and distortion artefacts consumed by reporting and plotting. It is the only module that converts sampled observations into baseline-aligned detection rows and per-flow distortion metrics.

## Inputs

- `data/processed/{dataset_id}/baseline_flows.parquet` from `flow_construction`
- `data/processed/{dataset_id}/sampling_runs.parquet` from `sampling`
- Sampled packet tables referenced by the sampling manifest
- Shared methodology settings:
  - `flow_key_fields`
  - `size_basis`
  - `byte_basis`

The implementation reads sampled packet tables directly. It does not use sampled-flow tables for metric scoring.

## Outputs

- `results/tables/{dataset_id}_metric_summary.parquet`
- `results/tables/{dataset_id}_flow_metrics.parquet`

The summary table contains one row per sampling rate per requested size basis with:

- `dataset_id`
- `sampling_rate`
- `sampling_method`
- `random_seed`
- `baseline_flow_count`
- `detected_flow_count`
- `undetected_flow_count`
- `flow_detection_rate`
- `sampled_packet_count`
- `sampled_flow_count`
- `size_basis`
- `byte_basis`

The per-flow table contains one row per baseline flow per sampling rate per requested size basis with:

- `dataset_id`
- `sampling_rate`
- `sampling_method`
- `random_seed`
- `flow_id`
- `detection_status`
- `size_basis`
- `byte_basis`
- `baseline_size`
- `sampled_size_estimate`
- `baseline_duration_seconds`
- `sampled_duration_seconds`
- `baseline_sending_rate`
- `sampled_sending_rate`
- `flow_size_overestimation_factor`
- `flow_duration_underestimation_factor`
- `flow_sending_rate_overestimation_factor`

## Methodology and implementation logic

- The `1:1` full-trace baseline is the only ground truth.
- Each sampled eligible packet is matched back to a baseline flow by:
  - the configured directional flow key
  - inclusion within that baseline flow's `[start_timestamp_us, end_timestamp_us]` interval
  - a per-key backward as-of join on `start_timestamp_us`, followed by an explicit `timestamp_us <= end_timestamp_us` interval check
- If a sampled eligible packet cannot be matched to any baseline flow interval for its key, the module raises an error rather than silently dropping it.
- Flow detection rate is computed over all baseline flows:
  - `detected_flow_count / baseline_flow_count`
  - baseline flows with no matched sampled packets are emitted as `undetected`
- The module emits one per-flow row for every baseline flow at every sampling rate and requested size basis, which keeps the undetected denominator explicit.
- Execution is per sampling rate:
  - sampled packets are aggregated to per-flow observations with Polars rather than expanded into Python packet lists
  - each sampling-rate flow-metric slice is written to a temporary Parquet part before the final `flow_metrics.parquet` file is assembled
- Size estimation follows the MVP formulas:
  - packets: `observed_sampled_packet_count * sampling_rate`
  - bytes: `observed_sampled_byte_count * sampling_rate`
- Sampled duration is derived from sampled packets only.
- Zero-duration handling is explicit:
  - sampled or baseline durations of `0` keep rate-based or duration-ratio metrics null where the denominator would be zero
  - size ratios remain defined because baseline flow size is always positive for emitted flows
- When `size_basis` is `both`, summary rows are duplicated across `packets` and `bytes`. Detection counts remain the same, but the unit label stays explicit.

## Upstream and downstream contracts

- Upstream contract:
  - `flow_construction` must provide a non-empty baseline flow table with interval bounds and size columns.
  - `sampling` must provide a non-empty sampling manifest whose `sampled_packets_path` values point to readable Parquet files.
- Downstream contract:
  - `plotting` consumes `metric_summary.parquet`.
  - Result-writing or later analysis code can consume either the summary table or the per-flow table depending on whether it needs completeness aggregates or flow-level distortion details.

## Assumptions and limitations

- Matching assumes baseline flows with the same directional flow key do not overlap in time. The baseline construction logic currently guarantees that for a fixed key and timeout.
- The module matches sampled packets to baseline intervals, not to sampled-flow fragments.
- Detection status is binary per baseline flow for a given sampling rate: at least one matched sampled packet means `detected`.
- The summary table currently contains only detection-oriented aggregates; it does not yet include means or quantiles of the distortion metrics.
- Large datasets still require substantial memory during the per-rate joins, but the module no longer accumulates all sampling rates and all per-flow rows in Python memory at once.
