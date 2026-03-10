# Dataset Registry Module

## Purpose

The `dataset_registry` module is the planned entry point for dataset declarations and validation metadata. It should define which raw capture files belong to a dataset and record the provenance needed for downstream analysis.

## Stage 1 scope

At Stage 1, this module is expected to provide configuration and schema placeholders only. It does not yet vet external datasets or inspect packet files.

## Inputs

- Dataset identifiers from config.
- Raw input paths.
- Optional metadata such as capture year, domain, compression wrapper, and provenance notes.

## Outputs

- Normalised dataset records that downstream stages can consume.
- A clear contract for what ingest requires from dataset declarations.

## Methodology and implementation logic

- Full-trace captures are required for the `1:1` baseline.
- Sampled public traces must not be treated as ground truth.
- Dataset metadata should preserve uncertainty instead of pretending absent documentation is confirmed.

## Assumptions and limitations

- Stage 1 does not yet implement full acceptance checks such as timestamp quality or documented losslessness.
- File probing and checksum generation belong to later work once ingest is implemented.

## Upstream and downstream contracts

- Upstream: `shared` and user-provided config.
- Downstream: `ingest`.
