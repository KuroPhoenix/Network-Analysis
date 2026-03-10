# Sampling Module Changelog

## 2026-03-10

### Implementation

1. Purpose of modification: implement the local MVP sampling module.
2. What changed: added per-rate sampled-packet tables, sampled-flow reconstruction from sampled packets only, deterministic systematic sampling, optional seeded random sampling, and a Parquet sampling manifest.
3. Impact on other pipeline modules: `metrics` can now consume stable per-rate sampled packet and sampled flow artefacts instead of placeholder contracts.
4. Required maintenance or follow-up updates: keep the sampled-flow schema and manifest aligned if new sampling methods or alternative size estimators are introduced.

### Documentation Audit

1. Purpose of modification: align sampling docs with the current runtime behavior.
2. What changed: documented the exact per-rate artefact names, the baseline-flow gate, the random-sampling selection semantics, and the distinction between diagnostic sampled flows and metric-scoring inputs.
3. Impact on other pipeline modules: no runtime behavior changed; `metrics` and future maintainers now have clearer documentation for what this module does and does not guarantee.
4. Required maintenance or follow-up updates: update the docs if the sampling method set, empty-schema assumptions, or estimator formulas change.
