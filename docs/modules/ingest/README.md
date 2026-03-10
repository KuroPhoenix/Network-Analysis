# Ingest Module

## Purpose

The `ingest` module is responsible for discovering raw inputs and preparing staged packet-capture files without modifying the original raw artefacts.

## Stage 1 scope

At Stage 1, this module is a documented placeholder. The real file discovery and decompression logic is not implemented yet.

## Inputs

- Dataset records from `dataset_registry`.
- Raw capture paths under the immutable raw-data area.
- Supported capture or archive formats once implemented.

## Outputs

- Staged capture file records.
- Ingest metadata such as source path, staged path, detected format, compression wrapper, and dataset identifier.

## Methodology and implementation logic

- Raw inputs must remain immutable.
- Decompression must be explicit and reproducible.
- Failures should be surfaced clearly rather than skipped silently.

## Assumptions and limitations

- Stage 1 does not yet read files, decompress archives, or compute checksums.
- Parquet does not apply directly here because this stage produces staged capture files and manifest metadata rather than packet tables.

## Upstream and downstream contracts

- Upstream: `dataset_registry`.
- Downstream: `packet_extraction`.
