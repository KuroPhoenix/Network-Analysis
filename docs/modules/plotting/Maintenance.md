# Plotting Module Maintenance

## Usage notes

- Keep plotting inputs read-only and derived strictly from metric outputs.
- Prefer deterministic filenames and predictable output locations.

## Maintenance guidelines

- Re-check labels and legends whenever metric definitions or unit bases change.
- Keep plotting logic separate from metric computation logic.

## Operational caveats

- Plotting bugs can misrepresent correct metrics, so treat label drift and unit confusion as correctness issues.

## Recommendations for future work

- Add a minimal detection-rate or distortion-factor plot once metrics are implemented.
- Add tests or snapshot checks for figure generation if the plotting layer grows.
