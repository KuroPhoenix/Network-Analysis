# Ingest Module

## Purpose

The `ingest` module prepares staged packet-capture files without modifying the original raw artefacts. It reads the dataset registry manifest, copies already-readable captures into the staged area, decompresses supported wrappers explicitly, and records the resulting staged files in a Parquet manifest.

## Current scope

This module is now implemented for the local MVP start. It supports direct `.pcap` and `.pcapng` inputs plus `.gz`, `.xz`, and `.zip` wrappers. It rejects `.rar` archives loudly because the local MVP does not ship extra archive tooling.

## Inputs

- Dataset records from `dataset_registry`.
- Raw capture paths under the immutable raw-data area.
- Supported capture or archive formats: `.pcap`, `.pcapng`, `.pcap.gz`, `.pcapng.gz`, `.xz`, `.zip`.

## Outputs

- Staged capture files under `data/staged/{dataset_id}/`
- `data/processed/{dataset_id}/ingest_manifest.parquet`
- Manifest fields include:
  - source and staged file paths
  - staging action
  - capture format
  - compression wrapper
  - source and staged sizes
  - SHA256 checksums for source and staged files

## Methodology and implementation logic

- Raw inputs must remain immutable.
- Decompression must be explicit and reproducible.
- Failures are surfaced clearly rather than skipped silently.
- Uncompressed captures are copied into the staged area so downstream parsing never mutates raw inputs in place.

## Assumptions and limitations

- `.zip` archives are supported only for members that end with `.pcap` or `.pcapng`.
- `wire_len` recovery or archive-specific metadata is not handled here; this stage only stages readable captures and records provenance.
- Parquet applies only to the ingest manifest; the staged capture files themselves remain packet-capture files.

## Upstream and downstream contracts

- Upstream: `dataset_registry`.
- Downstream: `packet_extraction`.
