# Metrics Module Maintenance

## Usage notes

- Keep completeness loss and metric distortion distinct in both tables and prose.
- Treat dropped undetected flows or denominator changes as methodology regressions.
- Always state the size basis when reading or reporting per-flow rows.

## Maintenance guidelines

- Re-check every formula against `AGENTS.md` and `docs/frozen/pipeline-mvp.md` before changing this module.
- Preserve the sampled-packet-to-baseline matching rule unless the repo explicitly adopts a different comparison contract.
- Revalidate zero-duration handling whenever duration, rate, or ratio formulas change.
- Keep summary-schema changes conservative because plotting and result-writeup consume it directly.
- Keep flow-key dtypes aligned across sampled-packet and baseline-flow tables before touching the matching logic; mixed integer widths can break the as-of join even when the values are equivalent.

## Operational caveats

- Silent unit drift between packets and bytes is a high-risk failure mode here.
- A sampled packet that falls outside all baseline intervals for its key currently raises. If that behavior changes, it must be documented as a methodology change.
- The module assumes baseline intervals are authoritative for matching sampled observations.
- Large datasets are processed per sampling rate and use temporary Parquet parts under `data/processed/{dataset_id}/_metrics_parts/`; the module removes that directory on success or failure, so leftover files there usually indicate an interrupted run.

## Recommendations for future work

- Add broader aggregate summaries only after deciding which ones are methodologically useful for the repo.
- If future work introduces alternative estimators, document them explicitly and avoid mixing them into the existing columns.
