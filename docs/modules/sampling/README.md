# Sampling Module

## Purpose

The `sampling` module generates the sampled packet artefacts used for every `1:X` comparison and also emits diagnostic sampled-flow reconstructions derived from those sampled packets only. It preserves the ground-truth-first workflow by requiring that the `1:1` baseline flow table already exists before any sampling run is emitted.

## Inputs

- `data/processed/{dataset_id}/packets.parquet` from `packet_extraction`
- `data/processed/{dataset_id}/baseline_flows.parquet` from `flow_construction`
- Shared sampling settings:
  - `rates`
  - `method`
  - `random_seed`
- Shared methodology settings:
  - `flow_key_fields`
  - `inactivity_timeout_seconds`
  - `size_basis`
  - `byte_basis`

## Outputs

- `data/processed/{dataset_id}/sampled_packets/`
- `data/processed/{dataset_id}/sampled_flows/`
- `data/processed/{dataset_id}/sampling_runs.parquet`

For each configured rate, the module writes:

- `data/processed/{dataset_id}/sampled_packets/{dataset_id}_{timeout}s_{rate}x_sampled_packets.parquet`
- `data/processed/{dataset_id}/sampled_flows/{dataset_id}_{timeout}s_{rate}x_sampled_flows.parquet`

The sampling manifest records:

- `dataset_id`
- `sampling_rate`
- `sampling_method`
- `random_seed`
- `sampled_packets_path`
- `sampled_flows_path`
- `sampled_packet_count`
- `flow_eligible_sampled_packet_count`
- `sampled_flow_count`
- `size_basis`
- `byte_basis`

## Methodology and implementation logic

- Every `1:X` run is evaluated relative to the already-built `1:1` baseline.
- The module always emits the `1:1` case because `sampling.normalized_rates()` prepends the baseline rate.
- Systematic sampling selects packets where `(packet_index - 1) % rate == 0`. This makes selection deterministic for a fixed canonical packet table.
- Random sampling independently selects each packet with probability `1 / rate` using `random.Random(random_seed + rate)`. The seed is therefore reproducible and rate-specific.
- Sampled packet tables retain the same canonical packet columns plus `sampling_rate`, `sampling_method`, and `random_seed`.
- Sampled-flow tables are rebuilt from sampled packets only by reusing the same flow-construction helpers and timeout semantics. Missing packets are not inferred from the baseline.
- After sampled flows are reconstructed, the module derives:
  - `sampled_packet_count`
  - `sampled_byte_count`
  - `estimated_packet_count = sampled_packet_count * rate`
  - `estimated_byte_count = sampled_byte_count * rate`
- Sampled flows are diagnostic outputs. They are not the authoritative source for baseline matching in `metrics`.

## Upstream and downstream contracts

- Upstream contract:
  - `packet_extraction` must have written a non-empty canonical packet table.
  - `flow_construction` must have written a non-empty baseline flow table. The module uses this as a ground-truth-first execution gate even though sampled-flow reconstruction itself starts from sampled packets.
- Downstream contract:
  - `metrics` reads the sampling manifest and sampled packet tables to compute detection and distortion metrics.
  - `metrics` does not assume sampled-flow IDs have any direct correspondence to baseline flow IDs.

## Assumptions and limitations

- Ineligible packets remain present in sampled packet tables because sampling is applied to the full packet stream, not just to flow-eligible packets.
- Sampled-flow tables may fragment a baseline flow if sampled packet gaps exceed the inactivity timeout. That is expected and is part of the measured effect rather than a reconstruction bug.
- The current empty sampled-flow schema is hard-coded for the default directional 5-tuple fields.
- Random sampling requires `sampling.random_seed`; otherwise the module raises rather than producing non-reproducible output.
