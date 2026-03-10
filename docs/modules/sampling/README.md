# Sampling Module

## Purpose

The `sampling` module will produce `1:X` sampled packet streams or sampled flow reconstructions that remain directly comparable to the `1:1` baseline.

## Current scope

This module is still a documented placeholder. No sampling emulation or sampled-trace ingestion logic is implemented yet.

## Inputs

- Canonical packet tables or another baseline-compatible packet source.
- Sampling rates such as `1:10` or `1:100`.
- One explicit sampling method.
- Optional random seed when the sampling method is stochastic.

## Outputs

- Sampled packet tables and or sampled flow tables.
- Sampling metadata recording dataset identifier, sampling rate, method, and seed when applicable.

## Methodology and implementation logic

- Every `1:X` case must compare directly against the `1:1` baseline.
- Sampled flows must be reconstructed from sampled packets, not by scaling full baseline flows directly.
- Externally supplied sampled traces must not be treated as ground truth.

## Assumptions and limitations

- This module does not yet implement deterministic or stochastic sampling procedures.
- Matching logic against the baseline belongs to `metrics`, not to this module.

## Upstream and downstream contracts

- Upstream: `packet_extraction`, `flow_construction`, `shared`.
- Downstream: `metrics`.
