# Ingest Module Maintenance

## Usage notes

- Keep staged files separate from raw files.
- Preserve source-to-staged traceability in every manifest record.

## Maintenance guidelines

- Revisit this module whenever the repo adds support for a new archive wrapper or capture format.
- Keep failure modes explicit so malformed inputs do not disappear silently.

## Operational caveats

- Never overwrite or mutate raw capture files.
- Do not mix staging metadata with later packet-table outputs.

## Recommendations for future work

- Add checksum tracking and deterministic staged filenames.
- Add small fixtures for discovery and decompression validation.
