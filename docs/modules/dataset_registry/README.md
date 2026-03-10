# Dataset Registry Module

## Purpose

The `dataset_registry` module is the entry point for dataset declarations and raw-file discovery. It records which capture or archive files belong to the configured dataset and persists the minimum provenance needed for downstream ingest and analysis.

## Current scope

This module is now implemented for the local MVP start. It validates the configured input directory and glob, discovers matching raw files deterministically, infers compression types from file names, detects capture formats from readable file headers when possible, and writes a Parquet registry manifest.

## Inputs

- Dataset identifiers from config.
- Raw input directory and discovery glob.
- Shared methodology settings that must remain visible: flow key, inactivity timeout, size basis, and byte basis.

## Outputs

- `data/processed/{dataset_id}/dataset_registry.parquet`
- One row per discovered raw file with:
  - deterministic discovery index
  - raw file path and size
  - capture format hint, detected from readable raw bytes when possible
  - inferred compression wrapper
  - explicit methodology settings copied from config

## Methodology and implementation logic

- Full-trace captures are required for the `1:1` baseline.
- Sampled public traces must not be treated as ground truth.
- Discovery is deterministic because downstream sampling and flow results must be reproducible.
- For directly readable captures and single-stream wrappers such as `.gz` and `.xz`, the module inspects the capture header instead of trusting the filename suffix. This keeps mislabeled but valid captures usable in the local pipeline.
- The registry preserves uncertainty explicitly: `capture_format_hint` is still a hint, not proof that a dataset satisfies year, losslessness, or timestamp-quality acceptance rules.

## Assumptions and limitations

- This module does not yet implement full dataset-acceptance vetting such as timestamp quality, documented losslessness, or capture year checks.
- Archive wrappers such as `.zip` and `.rar` still rely on later ingest handling rather than deep archive-member inspection here.
- Unsupported suffix patterns still fail loudly instead of being guessed.

## Upstream and downstream contracts

- Upstream: `shared` and user-provided config.
- Downstream: `ingest`.
