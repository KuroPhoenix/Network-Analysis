# Plotting Module Maintenance

## Usage notes

- Keep plotting inputs read-only and derived strictly from metric outputs.
- Prefer deterministic filenames and predictable output locations.
- Keep the rendered points traceable back to the exact metric rows used to build the figure.
- Keep line-plot aggregation rules explicit in code and docs.

## Maintenance guidelines

- Re-check labels and legends whenever metric definitions or unit bases change.
- Keep plotting logic separate from metric computation logic.
- Preserve the lightweight SVG path unless a heavier backend adds clear value without complicating local validation.
- Keep `plotting_summary.parquet` aligned with whatever rate-line figures are emitted.

## Operational caveats

- Plotting bugs can misrepresent correct metrics, so treat label drift and unit confusion as correctness issues.
- Detection-rate plots should not duplicate points across size bases when the metric itself is basis-independent.
- Duration plots and duration-factor plots should continue to deduplicate basis-independent rows deterministically.

## Recommendations for future work

- Add stronger snapshot or geometry checks if the plotting layer grows beyond the current line-plot and CDF path.
- Revisit plotting modes later only if the repo needs a smaller subset than the current active family.
