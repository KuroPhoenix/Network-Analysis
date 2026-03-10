# Packet Extraction Module

## Purpose

The `packet_extraction` module converts staged `PCAP` or `PCAPNG` files into the canonical packet table used by baseline flow construction, sampling, and metric matching. It is the first packet-scale Parquet artefact in the MVP and preserves full packet-stream order rather than pre-filtering down to only flow-eligible traffic.

## Inputs

- `data/processed/{dataset_id}/ingest_manifest.parquet` from `ingest`
- Staged capture files referenced by that manifest
- Shared methodology settings:
  - flow-key field names
  - byte basis
  - dataset identifier

The implementation requires the ingest manifest to provide at least:

- `staged_file`
- `capture_format`
- `source_discovery_index`
- `source_member_index`

## Outputs

- `data/processed/{dataset_id}/packets.parquet`
- `data/processed/{dataset_id}/packet_extraction_manifest.parquet`

The canonical packet table contains these columns:

- `dataset_id`
- `source_discovery_index`
- `source_member_index`
- `source_file`
- `packet_index`
- `source_packet_index`
- `timestamp_us`
- `timestamp`
- `captured_len`
- `wire_len`
- `protocol`
- `src_ip`
- `dst_ip`
- `src_port`
- `dst_port`
- `tcp_flags`
- `flow_eligible`
- `flow_ineligible_reason`

The extraction manifest currently records:

- `dataset_id`
- `source_file_count`
- `total_packets`
- `flow_eligible_packets`
- `flow_ineligible_packets`
- `earliest_timestamp`
- `latest_timestamp`

## Methodology and implementation logic

- Files are processed in ingest-manifest order: first by `source_discovery_index`, then by `source_member_index`.
- Packets inside each file are read in capture order and given a deterministic `source_packet_index`.
- The module assigns a global `packet_index` after concatenating all packet rows. Systematic sampling later depends on this index.
- `timestamp_us` is the canonical microsecond timestamp used for ordering and timeout comparisons. The `timestamp` column is a UTC datetime derived from it.
- The CPU reference parser is `dpkt`.
- The current eligibility rule matches the repo default directional 5-tuple:
  - IPv4 or IPv6 plus TCP or UDP produces `flow_eligible = true`.
  - Non-IP traffic and IP traffic without TCP or UDP are retained in the packet table but marked ineligible.
- `captured_len` is the explicit byte basis used by downstream byte-based metrics in the MVP.
- `wire_len` is currently emitted as null because this parser path does not recover a trustworthy original wire length.
- The module fails loudly on malformed or unreadable capture content instead of silently dropping packets.

## Upstream and downstream contracts

- Upstream contract:
  - `ingest` must already have written a non-empty manifest.
  - `staged_file` paths must exist and `capture_format` must be one of `pcap` or `pcapng`.
- Downstream contract:
  - `flow_construction` requires `packet_index`, `timestamp_us`, `timestamp`, `captured_len`, `wire_len`, `flow_eligible`, and the configured flow-key fields.
  - `sampling` expects the full packet table, including ineligible packets, so packet-selection semantics apply to the same packet stream as the baseline run.

## Assumptions and limitations

- The parser assumes Ethernet-encapsulated packets through `dpkt.ethernet.Ethernet`.
- Only TCP and UDP packets over IPv4 or IPv6 are eligible for the default flow reconstruction path.
- `tcp_flags` are captured for TCP packets only and stored as a stringified integer flag value.
- The module does not currently emit richer parser diagnostics such as decode-error counters or link-layer metadata beyond what is needed for the MVP.
