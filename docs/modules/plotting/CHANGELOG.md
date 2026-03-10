# Plotting Module Changelog

## 2026-03-10

1. Purpose of modification: implement the optional MVP plotting module.
2. What changed: added a lightweight SVG renderer that consumes `metric_summary` and writes a deterministic flow-detection-rate plot without changing any metric semantics.
3. Impact on other pipeline modules: the demo pipeline can now exercise a complete path through plotting while keeping the plotting logic separate from metrics.
4. Required maintenance or follow-up updates: extend the module only when additional plots can be justified without hiding or redefining the underlying metric contract.
