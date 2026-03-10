# Packet Extraction Module

## Purpose

The `packet_extraction` module converts staged `PCAP` or `PCAPNG` captures into a canonical packet table suitable for baseline and sampled flow reconstruction. It keeps full packet-stream order, writes Parquet as the main intermediate format, and retains packets that are not eligible for the default directional 5-tuple so sampling still operates on the full packet stream.

## Current scope

This module is now implemented for the local MVP start. It uses `dpkt` as a CPU reference parser for `PCAP` and `PCAPNG` and writes:

- `data/processed/{dataset_id}/packets.parquet`
- `data/processed/{dataset_id}/packet_extraction_manifest.parquet`

## Inputs

- Staged packet-capture files from `ingest`.
- Parser configuration and shared schema definitions.

## Outputs

- Canonical packet tables written as Parquet.
- Extraction metadata including total packet count and flow-eligible/ineligible packet counts.
- Explicit provenance-order columns (`source_discovery_index`, `source_member_index`, `source_packet_index`) plus canonical `timestamp_us`.

## Methodology and implementation logic

- Preserve packet order semantics.
- Freeze packet order on explicit source-file discovery order plus source packet order, not on timestamp sorting.
- Preserve timestamp fidelity.
- Extract the fields needed for the directional 5-tuple flow key and later flow metrics.
- Preserve all packets in the canonical table so later sampling operates on the full trace rather than a pre-filtered subset.
- Mark packets as `flow_eligible = false` when they lack the full default directional 5-tuple. In the current MVP this mainly affects non-IP packets and IP packets whose transport protocol is not TCP or UDP.
- Use `captured_len` as the explicit byte basis when byte-based size metrics are requested later. `wire_len` remains null unless the parser exposes an original on-wire length explicitly.

## Assumptions and limitations

- The current parser records `timestamp_us` as the canonical ordering and time-comparison field. The human-readable `timestamp` column is derived from it.
- Default flow reconstruction support is currently constrained to packets with a full TCP or UDP directional 5-tuple.
- Unsupported packets are retained for ordering and sampling but excluded from default flow reconstruction via the eligibility flags.

## Upstream and downstream contracts

- Upstream: `ingest`, `shared`.
- Downstream: `flow_construction`, `sampling`.
