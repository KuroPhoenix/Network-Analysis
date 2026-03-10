# Flow Construction Module Maintenance

## Usage notes

- Treat timeout changes as methodology changes and document them explicitly.
- Keep the flow key identical across baseline and sampled reconstructions unless the experiment explicitly studies another key.
- Re-run boundary coverage whenever ordering, timeout comparison, or byte accounting changes.

## Maintenance guidelines

- Preserve the `gap > timeout` split rule unless the repo methodology changes.
- Keep `timestamp_us` and `packet_index` in sync with packet-extraction semantics.
- Revalidate determinism after any performance optimization, chunking attempt, or parser change.
- Keep zero-duration handling explicit. Do not coerce undefined sending rates to zero.

## Operational caveats

- This module defines the only ground-truth baseline. A subtle bug here contaminates every downstream `1:X` comparison.
- Matching sampled observations by `flow_id` alone is not valid. Downstream logic must continue to match by shared flow key and time interval.
- Eligible packets with null key fields are rejected by design.

## Recommendations for future work

- Add more targeted fixtures around multi-file ordering, timeout boundaries, and repeated directional keys if flow construction logic changes.
- Extend byte-basis support only when the new definition is made explicit in shared config, tests, and module docs.
