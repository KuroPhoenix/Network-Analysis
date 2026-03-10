# Ingest Module Maintenance

## Usage notes

- Run `dataset_registry` before this module. `ingest` fails if the registry manifest is missing or empty.
- Treat the staged area as reproducible working output, not as a new source of truth.
- Keep raw dataset files outside normal Git history; this module is designed to copy or extract from them without mutating them.

## Maintenance guidelines

- Preserve deterministic staged naming whenever new archive formats or multi-member wrappers are added.
- Keep checksum collection for both source and staged artefacts so provenance remains auditable.
- If new compression types are introduced, update both the implementation and this documentation together.
- Keep extraction logic explicit in this module rather than moving archive handling into the driver or packet parser.
- Keep staged capture-format detection header-based whenever the staged bytes are directly readable.

## Operational caveats

- ZIP archives may emit multiple staged files; downstream packet ordering depends on `source_discovery_index` and `source_member_index`.
- `.rar` currently fails by design. Do not silently add shell-dependent fallback behavior without documenting the new dependency.
- Staging does not verify packet-level integrity. A successfully staged file can still fail later in `packet_extraction`.
- Progress bars are runtime feedback only. They must remain optional and must not become a control surface for methodology or retry logic.

## Recommendations for future work

- Add optional staged-file reuse or cleanup policies only if they remain deterministic and easy to reason about.
- If richer archive metadata becomes important, extend the manifest instead of relying on filenames alone.
