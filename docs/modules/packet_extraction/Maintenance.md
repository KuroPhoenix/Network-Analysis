# Packet Extraction Module Maintenance

## Usage notes

- Treat `timestamp_us` and `packet_index` as canonical. Downstream timeout handling and systematic sampling both depend on them.
- Keep the canonical packet schema stable once downstream modules depend on it.
- Preserve all packets in the packet table, even when they are not flow-eligible under the default 5-tuple.

## Maintenance guidelines

- If parser backends change, revalidate timestamp precision, packet ordering, TCP/UDP eligibility, and `captured_len` semantics.
- Keep `flow_ineligible_reason` values explicit and documented when adding new ineligibility cases.
- Update this module and `shared` together when canonical packet fields or byte-basis assumptions change.
- Keep the parser contract aligned with the staged `capture_format` values produced by `ingest`.
- Preserve ingest-manifest ordering when optimizing extraction internals. The current global `packet_index` depends on append order, not a later repair step.

## Operational caveats

- A packet row being present does not imply it participates in baseline flow construction.
- Silent packet drops are methodology defects here because they would distort both baseline and sampled packet streams.
- `wire_len` is intentionally null in the current CPU reference path. Do not repurpose it for another byte meaning.
- Progress bars are operator feedback only. They must not become a source of ordering, retry, or packet-selection logic.
- Per-file runtime logs are also operational feedback only. They must stay independent from packet parsing and retry decisions.

## Recommendations for future work

- Add parser diagnostics only if they can be kept lightweight and clearly separated from the canonical packet schema.
- Extend protocol support only when the repo adopts an explicit non-TCP/UDP flow-key contract.
