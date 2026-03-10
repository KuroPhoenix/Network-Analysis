# Packet Extraction Module Maintenance

## Usage notes

- Keep the canonical packet schema stable once downstream stages depend on it.
- Add new packet fields only when their downstream use is clear and documented.

## Maintenance guidelines

- Review timestamp handling carefully after any parser or backend change.
- Keep packet-order guarantees explicit in tests and documentation.

## Operational caveats

- Packet extraction is a correctness-critical boundary. Small timestamp or field-mapping errors will propagate into every later metric.

## Recommendations for future work

- Add fixtures that prove field extraction on tiny `PCAP` and `PCAPNG` examples.
- Add schema validation tests for required packet columns.
