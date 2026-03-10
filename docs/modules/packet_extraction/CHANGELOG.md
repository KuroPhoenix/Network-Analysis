# Packet Extraction Module Changelog

## 2026-03-10

### Implementation

1. Purpose of modification: turn packet extraction into the first Parquet-producing analysis step.
2. What changed: implemented `dpkt`-based `PCAP`/`PCAPNG` parsing, deterministic packet indexing, explicit provenance-order columns, eligibility flags for default flow reconstruction, and a Parquet extraction manifest. The module now leaves `wire_len` null unless a real on-wire value is available and uses `captured_len` as the visible byte basis.
3. Impact on other pipeline modules: `flow_construction` and `sampling` can now consume a stable canonical packet table instead of raw capture files.
4. Required maintenance or follow-up updates: revisit protocol eligibility and byte accounting if the repo later adopts a wider flow-key definition.

### Documentation Audit

1. Purpose of modification: align packet-extraction docs with the current schema and parser behavior.
2. What changed: documented the canonical packet columns, extraction-manifest columns, ordering rules, flow-eligibility semantics, and fail-loudly behavior on malformed captures.
3. Impact on other pipeline modules: no runtime behavior changed; downstream contracts are now explicit in module documentation.
4. Required maintenance or follow-up updates: keep the docs synchronized if canonical packet columns or parser assumptions change.
