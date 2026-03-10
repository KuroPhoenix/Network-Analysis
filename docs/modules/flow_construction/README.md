# Flow Construction Module

## Purpose

The `flow_construction` module builds the `1:1` ground-truth baseline flow table from the canonical packet table. It applies the configured directional flow key and inactivity timeout to flow-eligible packets only, then writes one deterministic Parquet flow table for downstream sampling comparisons.

## Inputs

- `data/processed/{dataset_id}/packets.parquet` from `packet_extraction`
- Shared methodology settings:
  - `flow_key_fields`
  - `inactivity_timeout_seconds`
  - `size_basis`
  - `byte_basis`

The module requires these packet-table fields:

- `dataset_id`
- `packet_index`
- `timestamp_us`
- `timestamp`
- `captured_len`
- `wire_len`
- configured flow-key columns
- `flow_eligible`

## Outputs

- `data/processed/{dataset_id}/baseline_flows.parquet`

The baseline flow table contains:

- `dataset_id`
- `flow_id`
- configured flow-key columns
- `flow_sequence`
- `start_timestamp_us`
- `end_timestamp_us`
- `start_ts`
- `end_ts`
- `start_packet_index`
- `end_packet_index`
- `duration_seconds`
- `packet_count`
- `byte_count`
- `sending_rate_packets_per_second`
- `sending_rate_bytes_per_second`
- `size_basis`
- `byte_basis`

## Methodology and implementation logic

- `1:1` is the only ground-truth baseline in the MVP.
- The module filters to `flow_eligible = true` packets before reconstruction.
- Packets are sorted by the configured flow-key fields, then by `timestamp_us`, then by `packet_index`.
- A new flow starts when either:
  - the directional flow key changes, or
  - the packet gap for the current key is greater than `inactivity_timeout_seconds`
- Gaps exactly equal to the timeout stay in the same flow. Only gaps greater than the timeout split the flow.
- `flow_sequence` counts baseline-flow fragments within the same directional key.
- `flow_id` is assigned after sorting the finalized rows by `start_ts`, flow key, and `flow_sequence`, which makes the output deterministic for a fixed packet table.
- `byte_count` is computed from the configured byte basis. The current implementation supports `captured_len` only.
- Zero-duration flows are retained with `duration_seconds = 0.0` and null sending-rate fields.
- Single-packet flows remain valid baseline flows.

## Upstream and downstream contracts

- Upstream contract:
  - `packet_extraction` must already have written a non-empty canonical packet table.
  - Flow-eligible packets must not contain null values in the configured flow-key fields.
- Downstream contract:
  - `sampling` depends on this module as the explicit ground-truth gate, even though sampled-flow reconstruction is performed from sampled packets only.
  - `metrics` consumes the baseline flow intervals, sizes, and sending-rate columns directly.

## Assumptions and limitations

- The reference implementation is CPU-first and stateful by design for clarity and determinism.
- Baseline flow IDs are deterministic for a fixed input packet table but should not be treated as a substitute for re-matching sampled packets.
- Only the `captured_len` byte basis is supported.
- Errors in this module invalidate every downstream completeness and distortion result because all `1:X` runs compare back to this baseline.
