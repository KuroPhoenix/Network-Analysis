# Packet Extraction Module Maintenance

## Usage notes

- Keep the canonical packet schema stable once downstream modules depend on it.
- Preserve field names required by the directional 5-tuple contract.
- Keep packet-order columns deterministic because systematic packet sampling depends on them.

## Maintenance guidelines

- Keep backend-specific parser details isolated from downstream modules.
- Update this module and `shared` together when packet schema contracts change.
- If the parser backend changes, revalidate timestamp handling and the `flow_eligible` semantics on mixed packet captures.

## Operational caveats

- Do not silently drop malformed or unsupported packets without recording that fact.
- Avoid mixing packet and byte semantics in column names.
- A packet being present in the table does not imply it is eligible for the default flow key.

## Recommendations for future work

- Add richer extraction metadata if downstream debugging needs it.
- Extend protocol support only when the flow-key definition for non-TCP/UDP traffic is made explicit.
