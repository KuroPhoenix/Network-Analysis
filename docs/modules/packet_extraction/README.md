# Packet Extraction Module

## Purpose

The `packet_extraction` module will convert staged `PCAP` or `PCAPNG` captures into a canonical packet table suitable for baseline and sampled flow reconstruction.

## Stage 1 scope

At Stage 1, this module is a documented placeholder. Packet parsing and Parquet writing are not implemented yet.

## Inputs

- Staged packet-capture files from `ingest`.
- Parser configuration and shared schema definitions.

## Outputs

- Canonical packet tables, intended to be written as Parquet.
- Optional extraction metadata such as packet count and field availability.

## Methodology and implementation logic

- Preserve packet order semantics.
- Preserve timestamp fidelity.
- Extract the fields needed for the directional 5-tuple flow key and later flow metrics.
- Fail loudly when essential reconstruction fields cannot be derived.

## Assumptions and limitations

- Stage 1 does not yet choose a parsing backend.
- Schema details should remain aligned with the shared definitions once code exists.

## Upstream and downstream contracts

- Upstream: `ingest`, `shared`.
- Downstream: `flow_construction`, `sampling`.
