# Plotting Module Changelog

## 2026-03-12

1. Purpose of modification: align plotting outputs with the active architecture's declared plot families.
2. What changed: expanded the plotting module from one detection-rate SVG to the full current family of per-rate line plots plus distortion-factor CDF plots, added a `plotting_summary.parquet` companion table, and converged plot paths onto `results/<dataset_id>/plots/`.
3. Impact on other pipeline modules: plotting still consumes stored metric outputs only and does not change any metric formulas or completeness semantics, but downstream users now get a fuller active-architecture figure set from the same metric tables.
4. Required maintenance or follow-up updates: if future work changes the aggregation used for any line plot, update both the plotting summary schema and this module README in the same slice.

## 2026-03-10

1. Purpose of modification: implement the optional MVP plotting module.
2. What changed: added a lightweight SVG renderer that consumes `metric_summary` and writes a deterministic flow-detection-rate plot without changing any metric semantics.
3. Impact on other pipeline modules: the demo pipeline can now exercise a complete path through plotting while keeping the plotting logic separate from metrics.
4. Required maintenance or follow-up updates: extend the module only when additional plots can be justified without hiding or redefining the underlying metric contract.
