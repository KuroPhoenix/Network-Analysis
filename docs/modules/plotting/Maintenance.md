# Plotting Module Maintenance

## Usage notes

- Keep plotting inputs read-only and derived strictly from metric outputs.
- Prefer deterministic filenames and predictable output locations.
- Keep the rendered points traceable back to the exact metric rows used to build the figure.

## Maintenance guidelines

- Re-check labels and legends whenever metric definitions or unit bases change.
- Keep plotting logic separate from metric computation logic.
- Preserve the lightweight SVG path unless a heavier backend adds clear value without complicating local validation.

## Operational caveats

- Plotting bugs can misrepresent correct metrics, so treat label drift and unit confusion as correctness issues.
- Detection-rate plots should not duplicate points across size bases when the metric itself is basis-independent.

## Recommendations for future work

- Add distortion-factor plots only after the current SVG contract remains easy to validate and maintain.
- Add stronger snapshot or geometry checks if the plotting layer grows beyond the current single-figure path.
