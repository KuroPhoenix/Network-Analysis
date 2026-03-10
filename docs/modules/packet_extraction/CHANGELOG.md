# Packet Extraction Module Changelog

## 2026-03-10

### Runtime and Integration

1. Purpose of modification: make packet extraction observable during long runs and align it with header-based capture-format detection upstream.
2. What changed: added lightweight per-file progress reporting and documented that `capture_format` in the ingest manifest is now resolved from staged capture bytes rather than only from filename suffixes.
3. Impact on other pipeline modules: no metric or packet semantics changed, but extraction now handles mislabeled captures correctly when upstream staging resolves the true format.
4. Required maintenance or follow-up updates: keep progress reporting lightweight and keep the ingest-manifest format contract synchronized with any future parser changes.

### Performance

1. Purpose of modification: reduce packet-extraction overhead on large traces without changing packet semantics.
2. What changed: switched the in-memory packet build path to column-oriented accumulation, derived UTC datetimes from `timestamp_us` in Polars, removed the redundant post-build resort, and reduced repeated manifest-count scans when writing extraction metadata.
3. Impact on other pipeline modules: downstream modules still receive the same canonical packet schema and deterministic packet ordering, but large local runs spend less time and memory in extraction.
4. Required maintenance or follow-up updates: if extraction becomes chunked in the future, preserve the same global packet ordering before assigning `packet_index`.

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
