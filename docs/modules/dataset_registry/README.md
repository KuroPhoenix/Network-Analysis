# Dataset Registry Module

## Purpose

The `dataset_registry` module is the entry point for dataset declarations and raw-file discovery. It records which capture or archive files belong to the configured dataset and persists the minimum provenance needed for downstream ingest and analysis.

## Current scope

This module is now implemented for the local MVP start. It validates the configured input directory and glob, discovers matching raw files deterministically, infers capture and compression types from file names, and writes a Parquet registry manifest.

## Inputs

- Dataset identifiers from config.
- Raw input directory and discovery glob.
- Shared methodology settings that must remain visible: flow key, inactivity timeout, size basis, and byte basis.

## Outputs

- `data/processed/{dataset_id}/dataset_registry.parquet`
- One row per discovered raw file with:
  - deterministic discovery index
  - raw file path and size
  - inferred capture format hint
  - inferred compression wrapper
  - explicit methodology settings copied from config

## Methodology and implementation logic

- Full-trace captures are required for the `1:1` baseline.
- Sampled public traces must not be treated as ground truth.
- Discovery is deterministic because downstream sampling and flow results must be reproducible.
- The registry preserves uncertainty explicitly: file-name inference is stored as a hint, not as proof that a dataset satisfies year, losslessness, or timestamp-quality acceptance rules.

## Assumptions and limitations

- This module does not yet implement full dataset-acceptance vetting such as timestamp quality, documented losslessness, or capture year checks.
- Capture-format inference is based on file suffixes, not deep file introspection.
- Unsupported suffix patterns fail loudly instead of being guessed.

## Upstream and downstream contracts

- Upstream: `shared` and user-provided config.
- Downstream: `ingest`.
