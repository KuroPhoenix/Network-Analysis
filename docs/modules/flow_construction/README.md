# Flow Construction Module

## Purpose

The `flow_construction` module will reconstruct directional `1:1` baseline flows from canonical packet tables using the shared flow key and inactivity timeout rules.

## Stage 1 scope

At Stage 1, this module is a documented placeholder. Baseline flow reconstruction logic is not implemented yet.

## Inputs

- Canonical packet tables from `packet_extraction`.
- Explicit flow key definition, defaulting to the directional 5-tuple.
- Inactivity timeout, defaulting to `15` seconds unless config overrides it.
- Explicit size basis selection.

## Outputs

- Baseline flow tables for the `1:1` ground-truth case.
- Flow-level metadata needed by later sampling and metric stages.

## Methodology and implementation logic

- `1:1` is the only ground-truth baseline.
- Packet gaps of `15` seconds or less stay in the same flow unless config overrides the timeout explicitly.
- Gaps greater than the timeout terminate the current flow and start a new one.
- Single-packet flows remain valid flows.

## Assumptions and limitations

- Stage 1 does not yet reconstruct flows or write Parquet flow tables.
- Later implementations must keep packets and bytes explicitly separated when both are supported.

## Upstream and downstream contracts

- Upstream: `packet_extraction`, `shared`.
- Downstream: `sampling`, `metrics`.
