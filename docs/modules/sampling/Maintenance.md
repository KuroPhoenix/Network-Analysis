# Sampling Module Maintenance

## Usage notes

- Keep the sampling procedure explicit and reproducible.
- Record `sampling_method`, `sampling_rate`, and `random_seed` in any result discussion or debugging note.
- Remember that this module samples the full packet table, not only the flow-eligible subset.

## Maintenance guidelines

- When adding a new sampling method, document the exact packet-selection rule and update the manifest schema if needed.
- Keep the `1:1` baseline rate in the emitted run set unless the repo methodology changes.
- Re-check sampled-flow reconstruction after any change to shared flow-construction helpers or timeout semantics.
- If the flow key changes, update both the sampled-flow schema and the docs together.

## Operational caveats

- Do not shortcut sampled-flow output by scaling baseline flows directly. That would violate the repo methodology.
- Do not treat sampled-flow IDs as baseline identifiers.
- The current empty sampled-flow schema assumes the default directional 5-tuple fields. A flow-key override needs a corresponding schema update.

## Recommendations for future work

- Add more fixture coverage for seeded random sampling once the repo wants broader stochastic validation.
- If larger studies need additional sampled-packet diagnostics, add them to the manifest or packet tables explicitly rather than relying on implicit naming conventions.
