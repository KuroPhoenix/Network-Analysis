# Ingest Module

## Purpose

The `ingest` module turns dataset-registry records into a deterministic staged capture set for the rest of the MVP. It preserves raw inputs as immutable source artefacts, stages readable capture files under `data/staged/{dataset_id}/`, and writes a Parquet manifest that records exactly what was copied or decompressed.

## Inputs

- `data/processed/{dataset_id}/dataset_registry.parquet` from `dataset_registry`
- Raw files referenced by the registry manifest
- Registry fields required by the implementation:
  - `dataset_id`
  - `raw_file`
  - `discovery_index`
  - `capture_format_hint`
  - `compression_type`

## Outputs

- Staged capture files under `data/staged/{dataset_id}/`
- `data/processed/{dataset_id}/ingest_manifest.parquet`

The ingest manifest records one row per staged capture member with these fields:

- `dataset_id`
- `source_discovery_index`
- `source_member_index`
- `source_file`
- `archive_member_path`
- `staged_file`
- `staging_action`
- `capture_format`
- `compression_type`
- `source_sha256`
- `staged_sha256`
- `source_size_bytes`
- `staged_size_bytes`

## Methodology and implementation logic

- Raw inputs remain immutable. Direct `.pcap` and `.pcapng` files are copied into the staged area rather than processed in place.
- Supported wrappers are handled explicitly:
  - `.gz` is decompressed to one staged capture file.
  - `.xz` is decompressed to one staged capture file.
  - `.zip` is scanned for members whose readable header bytes identify them as `pcap` or `pcapng`, and each matching member is extracted separately.
- Staged filenames are deterministic. They are prefixed with `source_discovery_index`, and ZIP members also include `source_member_index`.
- Capture format for staged files is detected from the readable staged bytes instead of trusting the staged filename suffix. This keeps mislabeled but valid captures usable after staging.
- The module computes SHA256 hashes for both the source artefact and the staged file so later runs can confirm provenance.
- Failures are loud. Unsupported archive types and archives with no usable capture members raise `ValueError`.

## Upstream and downstream contracts

- Upstream contract:
  - `dataset_registry` must already have produced a non-empty Parquet manifest.
  - Registry rows must point to readable raw files.
- Downstream contract:
  - `packet_extraction` reads `ingest_manifest.parquet`.
  - `packet_extraction` relies on `source_discovery_index`, `source_member_index`, `staged_file`, and `capture_format` to preserve deterministic packet ordering across staged files.

## Assumptions and limitations

- `.rar` archives are intentionally unsupported in the local MVP because the repo does not add extra archive tooling by default.
- `.zip` member selection uses readable header bytes, but it still only scans the immediate archive members that are present in the ZIP file.
- The module does not validate packet readability beyond producing staged files and format metadata. Actual packet parsing happens in `packet_extraction`.
- Repeated runs overwrite the same staged paths deterministically; the raw source artefacts remain unchanged.
