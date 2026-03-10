# Packet Extraction Module Changelog

## 2026-03-10

1. Purpose of modification: turn packet extraction into the first Parquet-producing analysis step.
2. What changed: implemented `dpkt`-based `PCAP`/`PCAPNG` parsing, deterministic packet indexing, eligibility flags for default flow reconstruction, and a Parquet extraction manifest.
3. Impact on other modules or pipeline stages: flow construction and sampling can now consume a stable canonical packet table instead of raw capture files.
4. Required maintenance or follow-up updates: revisit protocol eligibility and byte accounting if the repo later adopts a wider flow-key definition.
