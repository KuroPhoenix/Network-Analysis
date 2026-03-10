# Flow Construction Module

## Purpose

The `flow_construction` module reconstructs directional `1:1` baseline flows from canonical packet tables using the shared flow key and inactivity timeout rules.

## Current scope

This module is now implemented for the local CPU reference path. It consumes the canonical packet table, filters to flow-eligible packets, groups packets by the configured directional flow key, and splits each key into separate baseline flows when the inactivity gap is greater than the configured timeout.

## Inputs

- Canonical packet tables from `packet_extraction`.
- Explicit flow key definition, defaulting to the directional 5-tuple.
- Inactivity timeout, defaulting to `15` seconds unless config overrides it.
- Explicit size basis selection.

## Outputs

- `data/processed/{dataset_id}/baseline_flows.parquet`
- Baseline flow rows include:
  - directional flow-key fields
  - deterministic `flow_id`
  - per-key `flow_sequence`
  - canonical `start_timestamp_us` and `end_timestamp_us` bounds
  - start and end timestamps
  - start and end packet indexes
  - packet and byte counts
  - packet and byte sending rates
  - explicit `size_basis` and `byte_basis` metadata

## Methodology and implementation logic

- `1:1` is the only ground-truth baseline.
- Packet gaps of `15` seconds or less stay in the same flow unless config overrides the timeout explicitly.
- Gaps greater than the timeout terminate the current flow and start a new one.
- Single-packet flows remain valid flows.
- Canonical timeout comparisons use packet microsecond timestamps, while the human-readable datetime columns remain for inspection.
- Byte counts use the configured byte basis. In the current MVP that basis is `captured_len`.
- Zero-duration flows keep `duration_seconds = 0` and leave sending-rate columns undefined rather than forcing a numeric value.

## Assumptions and limitations

- The current implementation is CPU-first and iterates flow state in Python for determinism and clarity.
- Flow IDs are deterministic for a given packet table, but sampled-flow matching must still rely on shared flow-key and timestamp logic rather than assuming sampled runs know baseline IDs in advance.
- The byte-basis handling is currently limited to `captured_len`.

## Upstream and downstream contracts

- Upstream: `packet_extraction`, `shared`.
- Downstream: `sampling`, `metrics`.
