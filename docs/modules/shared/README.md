# Shared Module

## Purpose

The `shared` module is the common definitions layer for the local-first pipeline MVP. It centralises configuration structures, constants, enumerations, type hints, and schema contracts that every stage must use.

## Stage 1 scope

At Stage 1, this module is expected to hold shared definitions only. It does not parse packet captures or compute flow metrics.

## Inputs

- CLI arguments and config file values.
- Repository-wide methodology defaults.

## Outputs

- Normalised configuration objects.
- Shared constants and type aliases.
- Schema contracts for stage inputs and outputs.

## Methodology and implementation logic

- Default flow key is the directional 5-tuple unless a config override is made explicitly.
- Default inactivity timeout is `15` seconds unless config overrides it.
- `1:1` is the ground-truth baseline.
- Every `1:X` case must compare directly against the `1:1` baseline.
- Size basis must remain explicit.
- Raw inputs are treated as immutable.
- Parquet is the preferred main intermediate tabular format.

## Assumptions and limitations

- Stage 1 should expose the contracts cleanly, but later stages still need to implement real validation and runtime checks.
- Dataset-specific metadata rules are not fully implemented yet.

## Upstream and downstream contracts

- Upstream: none.
- Downstream: all pipeline modules depend on these definitions for consistent methodology and reproducibility.
