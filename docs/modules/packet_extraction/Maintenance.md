# Packet Extraction Module Maintenance

## Usage notes

- Treat `timestamp_us` and `packet_index` as canonical. Downstream timeout handling and systematic sampling both depend on them.
- Keep the canonical packet schema stable once downstream modules depend on it.
- Preserve all packets in the packet table, even when they are not flow-eligible under the default 5-tuple.

## Maintenance guidelines

- If parser backends change, revalidate timestamp precision, packet ordering, TCP/UDP eligibility, and `captured_len` semantics.
- Keep `flow_ineligible_reason` values explicit and documented when adding new ineligibility cases.
- Update this module and `shared` together when canonical packet fields or byte-basis assumptions change.

## Operational caveats

- A packet row being present does not imply it participates in baseline flow construction.
- Silent packet drops are methodology defects here because they would distort both baseline and sampled packet streams.
- `wire_len` is intentionally null in the current CPU reference path. Do not repurpose it for another byte meaning.

## Recommendations for future work

- Add parser diagnostics only if they can be kept lightweight and clearly separated from the canonical packet schema.
- Extend protocol support only when the repo adopts an explicit non-TCP/UDP flow-key contract.
