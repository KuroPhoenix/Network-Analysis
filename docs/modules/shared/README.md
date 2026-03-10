# Shared Module

## Purpose

The `shared` module is the common definitions layer for the local-first pipeline MVP. It centralises configuration structures, constants, enumerations, type hints, schema contracts, and dataset artifact paths that every pipeline module must use.

## Current scope

This module now holds the shared config, schema, type, constant, and artifact-path logic for the executable local MVP slices. It does not parse packet captures or compute flow metrics itself, but later modules now depend on it for resolved dataset artifact paths, the explicit byte-basis contract, and the documented baseline-flow, sampled-packet, sampled-flow, sampling-manifest, and metric-table schemas.

## Inputs

- CLI arguments and config file values.
- Repository-wide methodology defaults.

## Outputs

- Normalised configuration objects.
- Shared constants and type aliases.
- Schema contracts for module inputs and outputs.
- Resolved dataset artifact paths for staged, processed, and result outputs.
- Shared provenance-order schema fields used to keep packet ordering reproducible across multiple raw inputs.
- Shared baseline-flow and sampled-packet schema fields used to keep later sampled-flow matching methodologically consistent.
- Shared sampling-manifest and metric-table schemas used to keep per-rate analysis outputs explicit and auditable.

## Methodology and implementation logic

- Default flow key is the directional 5-tuple unless a config override is made explicitly.
- Default inactivity timeout is `15` seconds unless config overrides it.
- `1:1` is the ground-truth baseline.
- Every `1:X` case must compare directly against the `1:1` baseline.
- Size basis must remain explicit.
- Byte basis must remain explicit when bytes are requested.
- Packet ordering must remain reproducible when multiple raw files or archive members are staged.
- Raw inputs are treated as immutable.
- Parquet is the preferred main intermediate tabular format.
- Shared schemas should keep zero-duration and undefined-rate cases visible instead of coercing them into misleading numeric defaults.

## Assumptions and limitations

- The shared layer intentionally does not hide methodology decisions behind driver defaults; later modules still need to enforce their own runtime validation.
- Dataset-specific acceptance metadata rules are still incomplete; the shared layer only carries the fields needed for reproducible local execution.
- Schema definitions assume the default directional 5-tuple unless a config override is made and propagated deliberately.

## Upstream and downstream contracts

- Upstream: none.
- Downstream: all pipeline modules depend on these definitions for consistent methodology and reproducibility.
