# Sampling Module

## Purpose

The `sampling` module will produce `1:X` sampled packet streams or sampled flow reconstructions that remain directly comparable to the `1:1` baseline.

## Current scope

This module is now implemented for the local CPU reference path. It samples the canonical packet table for each configured rate, writes one sampled-packet table and one sampled-flow table per rate, and records a Parquet sampling manifest that points to those artefacts.

## Inputs

- Canonical packet tables or another baseline-compatible packet source.
- Sampling rates such as `1:10` or `1:100`.
- One explicit sampling method.
- Optional random seed when the sampling method is stochastic.

## Outputs

- `data/processed/{dataset_id}/sampled_packets/`
- `data/processed/{dataset_id}/sampled_flows/`
- `data/processed/{dataset_id}/sampling_runs.parquet`
- Sampling metadata records:
  - dataset identifier
  - sampling rate
  - sampling method
  - random seed when applicable
  - sampled packet and sampled flow paths
  - sampled packet and sampled flow counts

## Methodology and implementation logic

- Every `1:X` case must compare directly against the `1:1` baseline.
- Sampled flows must be reconstructed from sampled packets, not by scaling full baseline flows directly.
- Externally supplied sampled traces must not be treated as ground truth.
- Systematic sampling uses the deterministic dataset-wide `packet_index`.
- The `1:1` path is emitted through the same module so later stages can validate the no-loss reference case with the same artefact contract.

## Assumptions and limitations

- Sampled-flow tables are diagnostic outputs reconstructed from sampled packets only. They are intentionally allowed to split a baseline flow when sampled packet gaps exceed the inactivity timeout.
- Matching logic against the baseline belongs to `metrics`, not to this module.
- Random sampling is supported only when an explicit `sampling.random_seed` is configured.

## Upstream and downstream contracts

- Upstream: `packet_extraction`, `flow_construction`, `shared`.
- Downstream: `metrics`.
